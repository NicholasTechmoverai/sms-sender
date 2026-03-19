from tortoise.models import Model
from tortoise import fields
from tortoise.contrib.pydantic import pydantic_model_creator
from typing import Optional, List, Dict, Any, Union
from enum import Enum
import re

# Enums for standardized fields
class Department(str, Enum):
    ENGINEERING = "engineering"
    MARKETING = "marketing" 
    SALES = "sales"
    HR = "human_resources"
    FINANCE = "finance"
    RESEARCH = "research_development"
    OPERATIONS = "operations"
    IT = "information_technology"

class ExpertiseLevel(str, Enum):
    JUNIOR = "junior"
    MID = "mid_level" 
    SENIOR = "senior"
    LEAD = "lead"
    EXECUTIVE = "executive"

class Person(Model):
    """Creative Person/User model with rich attributes"""
    
    # Basic Information
    id = fields.IntField(pk=True)
    form_number = fields.CharField(max_length=50, unique=True, description="Unique form identifier")
    name = fields.CharField(max_length=100, index=True)
    email = fields.CharField(max_length=100, unique=True, index=True)
    age = fields.IntField(null=True)
    birth_date = fields.DateField(null=True)
    
    # Contact Information - NEW PHONE FIELD ADDED
    phone = fields.CharField(max_length=20, null=True, index=True, description="Contact phone number with country code")
    phone_country_code = fields.CharField(max_length=5, null=True, description="Country code extracted from phone")
    phone_verified = fields.BooleanField(default=False, description="Whether phone number is verified")
    alternative_phone = fields.CharField(max_length=20, null=True, description="Alternative contact number")
    
    # Location Information
    country = fields.CharField(max_length=100, index=True)
    city = fields.CharField(max_length=100, index=True)
    address = fields.TextField(null=True, description="Full address")
    postal_code = fields.CharField(max_length=20, null=True)
    timezone = fields.CharField(max_length=50, null=True)
    remote_worker = fields.BooleanField(default=False)
    latitude = fields.FloatField(null=True, description="Location latitude for geo queries")
    longitude = fields.FloatField(null=True, description="Location longitude for geo queries")
    
    # Professional Information
    department = fields.CharEnumField(Department, index=True)
    expertise_level = fields.CharEnumField(ExpertiseLevel, null=True)
    years_experience = fields.IntField(default=0)
    skills = fields.JSONField(default=list, description="List of skills")
    certifications = fields.JSONField(default=list)
    current_position = fields.CharField(max_length=100, null=True, description="Current job title")
    company = fields.CharField(max_length=100, null=True, description="Current company")
    
    # Personal Characteristics
    languages = fields.JSONField(default=list, description="Languages spoken")
    hobbies = fields.JSONField(default=list)
    personality_traits = fields.JSONField(default=list)
    favorite_color = fields.CharField(max_length=30, null=True)
    gender = fields.CharField(max_length=20, null=True)
    
    # Additional Metadata
    bio = fields.TextField(null=True)
    profile_picture_url = fields.CharField(max_length=500, null=True)
    is_active = fields.BooleanField(default=True)
    tags = fields.JSONField(default=list, description="Custom tags for categorization")
    notes = fields.TextField(null=True, description="Internal notes")
    
    # Communication Preferences
    sms_enabled = fields.BooleanField(default=True, description="Can receive SMS")
    whatsapp_enabled = fields.BooleanField(default=False, description="Has WhatsApp")
    preferred_contact_method = fields.CharField(max_length=20, default="sms", description="sms, email, whatsapp, phone")
    
    # Social Media
    linkedin_url = fields.CharField(max_length=255, null=True)
    github_url = fields.CharField(max_length=255, null=True)
    twitter_handle = fields.CharField(max_length=50, null=True)
    
    # Timestamps
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    last_contacted_at = fields.DatetimeField(null=True, description="Last time contacted via any channel")
    
    class Meta:
        table = "creative_users"
        ordering = ["name"]
        indexes = [
            ("country", "city"),  # Composite index for location queries
            ("department", "expertise_level"),  # Composite index for professional filters
            ("phone",),  # Index for phone lookups
            ("created_at",),  # Index for sorting by date
        ]
        
    def __str__(self):
        return f"{self.name} ({self.department}) - {self.country}"
    
    @property
    def skill_count(self) -> int:
        """Return number of skills"""
        return len(self.skills) if self.skills else 0
    
    @property
    def full_location(self) -> str:
        """Return full location string"""
        parts = []
        if self.city:
            parts.append(self.city)
        if self.country:
            parts.append(self.country)
        return ", ".join(parts)
    
    @property
    def full_address(self) -> Optional[str]:
        """Return full address if available"""
        if self.address:
            address_parts = [self.address]
            if self.city:
                address_parts.append(self.city)
            if self.postal_code:
                address_parts.append(self.postal_code)
            if self.country:
                address_parts.append(self.country)
            return ", ".join(address_parts)
        return None
    
    @property
    def formatted_phone(self) -> Optional[str]:
        """Return formatted phone number if available"""
        if not self.phone:
            return None
        # Simple formatting - you might want to use a library like phonenumbers for proper formatting
        if len(self.phone) > 10:
            return f"{self.phone[:3]} {self.phone[3:6]} {self.phone[6:]}"
        return self.phone
    
    @property
    def has_valid_phone(self) -> bool:
        """Check if phone number is valid (basic validation)"""
        if not self.phone:
            return False
        # Remove common separators
        cleaned = re.sub(r'[\s\-\(\)\+]', '', self.phone)
        return len(cleaned) >= 10 and cleaned.isdigit()
    
    @property
    def contact_methods(self) -> List[str]:
        """Return list of available contact methods"""
        methods = []
        if self.email:
            methods.append("email")
        if self.has_valid_phone:
            if self.sms_enabled:
                methods.append("sms")
            if self.whatsapp_enabled:
                methods.append("whatsapp")
        return methods

class PersonSearchEngine:
    """
    Creative search engine for finding people based on various criteria
    with pagination support
    """
    
    def __init__(self):
        self.query = None
        
    async def search_people(
        self,
        # Location filters
        country: Optional[str] = None,
        city: Optional[str] = None,
        
        # Professional filters
        department: Optional[Department] = None,
        expertise_level: Optional[ExpertiseLevel] = None,
        min_experience: Optional[int] = None,
        required_skills: Optional[List[str]] = None,
        company: Optional[str] = None,
        
        # Personal characteristics
        languages: Optional[List[str]] = None,
        hobbies: Optional[List[str]] = None,
        personality_trait: Optional[str] = None,
        min_age: Optional[int] = None,
        max_age: Optional[int] = None,
        
        # Contact filters - NEW
        has_phone: Optional[bool] = None,
        sms_enabled: Optional[bool] = None,
        phone_verified: Optional[bool] = None,
        country_code: Optional[str] = None,  # Filter by phone country code
        
        # General search
        name_contains: Optional[str] = None,
        email_contains: Optional[str] = None,
        tags: Optional[List[str]] = None,
        is_active: bool = True,
        
        # Pagination
        limit: int = 10,
        offset: int = 0,
        
        # Sorting
        sort_by: str = "name",
        sort_order: str = "asc"
    ) -> Dict[str, Any]:
        """
        Search for people with multiple filters and pagination
        
        Returns:
            Dictionary containing results, total count, and pagination info
        """
        # Start with base query
        self.query = Person.filter(is_active=is_active)
        
        # Apply location filters
        if country:
            self.query = self.query.filter(country__icontains=country)
        if city:
            self.query = self.query.filter(city__icontains=city)
            
        # Apply professional filters
        if department:
            self.query = self.query.filter(department=department)
        if expertise_level:
            self.query = self.query.filter(expertise_level=expertise_level)
        if min_experience is not None:
            self.query = self.query.filter(years_experience__gte=min_experience)
        if company:
            self.query = self.query.filter(company__icontains=company)
        if required_skills:
            # People who have ALL required skills
            for skill in required_skills:
                self.query = self.query.filter(skills__contains=skill)
                
        # Apply personal characteristics
        if languages:
            for lang in languages:
                self.query = self.query.filter(languages__contains=lang)
        if hobbies:
            for hobby in hobbies:
                self.query = self.query.filter(hobbies__contains=hobby)
        if personality_trait:
            self.query = self.query.filter(personality_traits__contains=personality_trait)
        if min_age is not None:
            self.query = self.query.filter(age__gte=min_age)
        if max_age is not None:
            self.query = self.query.filter(age__lte=max_age)
            
        # Apply contact filters - NEW
        if has_phone is not None:
            if has_phone:
                self.query = self.query.exclude(phone__isnull=True).exclude(phone="")
            else:
                self.query = self.query.filter(phone__isnull=True)
        if sms_enabled is not None:
            self.query = self.query.filter(sms_enabled=sms_enabled)
        if phone_verified is not None:
            self.query = self.query.filter(phone_verified=phone_verified)
        if country_code:
            self.query = self.query.filter(phone__startswith=country_code)
            
        # Apply general search
        if name_contains:
            self.query = self.query.filter(name__icontains=name_contains)
        if email_contains:
            self.query = self.query.filter(email__icontains=email_contains)
        if tags:
            for tag in tags:
                self.query = self.query.filter(tags__contains=tag)
            
        # Get total count before pagination
        total_count = await self.query.count()
        
        # Apply sorting
        if sort_order.lower() == "desc":
            sort_field = f"-{sort_by}"
        else:
            sort_field = sort_by
        self.query = self.query.order_by(sort_field)
        
        # Apply pagination
        self.query = self.query.offset(offset).limit(limit)
        
        # Execute query
        results = await self.query
        
        # Calculate pagination info
        has_next = total_count > offset + limit
        has_previous = offset > 0
        total_pages = (total_count + limit - 1) // limit
        current_page = (offset // limit) + 1
        
        return {
            "results": results,
            "pagination": {
                "total_count": total_count,
                "limit": limit,
                "offset": offset,
                "current_page": current_page,
                "total_pages": total_pages,
                "has_next": has_next,
                "has_previous": has_previous
            },
            "filters_applied": {
                "country": country,
                "city": city,
                "department": department,
                "expertise_level": expertise_level,
                "min_experience": min_experience,
                "required_skills": required_skills,
                "languages": languages,
                "hobbies": hobbies,
                "personality_trait": personality_trait,
                "age_range": f"{min_age}-{max_age}" if min_age or max_age else None,
                "name_contains": name_contains,
                "has_phone": has_phone,
                "sms_enabled": sms_enabled
            }
        }
    
    async def search_by_phone(self, phone_number: str, exact_match: bool = True) -> Optional[Person]:
        """
        Find a person by phone number
        
        Args:
            phone_number: Phone number to search for
            exact_match: If True, search for exact match; if False, search for partial match
        """
        if exact_match:
            return await Person.filter(phone=phone_number).first()
        else:
            # Search for phone numbers containing the string
            return await Person.filter(phone__icontains=phone_number).first()
    
    async def get_users_with_phone_numbers(
        self,
        verified_only: bool = False,
        sms_enabled_only: bool = True,
        limit: int = 100,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Get users who have phone numbers, with optional filters
        Useful for SMS campaigns
        """
        self.query = Person.exclude(phone__isnull=True).exclude(phone="")
        
        if verified_only:
            self.query = self.query.filter(phone_verified=True)
        
        if sms_enabled_only:
            self.query = self.query.filter(sms_enabled=True)
        
        total_count = await self.query.count()
        results = await self.query.offset(offset).limit(limit)
        
        return {
            "results": results,
            "total_count": total_count,
            "limit": limit,
            "offset": offset
        }
    
    async def search_by_skill_proficiency(
        self, 
        skills: List[str], 
        min_skill_count: int = 1,
        limit: int = 10,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Find people who have at least min_skill_count from the provided skills list
        """
        from tortoise.expressions import Q
        
        # Build OR condition for skills
        skill_conditions = Q()
        for skill in skills:
            skill_conditions |= Q(skills__contains=skill)
            
        query = Person.filter(skill_conditions).filter(is_active=True)
        
        # We need to filter Python-side for min_skill_count
        # This is simplified - in production you might want a raw SQL approach
        all_results = await query
        filtered_results = [
            p for p in all_results 
            if len([s for s in p.skills if s in skills]) >= min_skill_count
        ]
        
        total_count = len(filtered_results)
        paginated_results = filtered_results[offset:offset + limit]
        
        return {
            "results": paginated_results,
            "total_count": total_count,
            "limit": limit,
            "offset": offset
        }
    
    async def find_similar_people(self, person_id: int, limit: int = 5) -> List[Person]:
        """
        Find people similar to a given person based on department, skills, and location
        """
        person = await Person.get(id=person_id)
        
        # Find people in same department with similar skills
        similar = await Person.filter(
            department=person.department,
            is_active=True
        ).exclude(id=person_id).limit(limit * 2)
        
        # Score and sort by similarity
        scored_people = []
        for candidate in similar:
            score = 0
            # Same country bonus
            if candidate.country == person.country:
                score += 3
            # Same city bonus
            if candidate.city == person.city:
                score += 2
            # Skill overlap
            common_skills = set(candidate.skills) & set(person.skills)
            score += len(common_skills) * 2
            # Similar expertise level
            if candidate.expertise_level == person.expertise_level:
                score += 1
                
            scored_people.append((candidate, score))
        
        # Sort by score and return top matches
        scored_people.sort(key=lambda x: x[1], reverse=True)
        return [p[0] for p in scored_people[:limit]]

# # Create Pydantic models for API responses
# Person_Pydantic = pydantic_model_creator(Person, name="Person")
# PersonIn_Pydantic = pydantic_model_creator(Person, name="PersonIn", exclude_readonly=True)

# # Phone-specific Pydantic model for SMS operations
# PersonSMS_Pydantic = pydantic_model_creator(
#     Person, 
#     name="PersonSMS",
#     include=("id", "name", "phone", "phone_verified", "sms_enabled", "country")
# )