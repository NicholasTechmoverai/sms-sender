from fastapi import APIRouter, Request, Query, HTTPException
from typing import Optional, List
from core.logger import setup_logger
from core.limiter import limiter
from models.index import PersonSearchEngine, Department, ExpertiseLevel

user_router = APIRouter(prefix="/users", tags=["Users"])
logger = setup_logger(__name__)

@user_router.get("/search")
@limiter.limit("30/minute")
async def search_users(
    request: Request,
    # Location filters
    country: Optional[str] = Query(None, description="Filter by country"),
    city: Optional[str] = Query(None, description="Filter by city"),
    
    # Professional filters
    department: Optional[Department] = Query(None, description="Filter by department"),
    expertise_level: Optional[ExpertiseLevel] = Query(None, description="Filter by expertise level"),
    min_experience: Optional[int] = Query(None, description="Minimum years of experience"),
    required_skills: Optional[List[str]] = Query(None, description="Required skills (comma-separated)"),
    company: Optional[str] = Query(None, description="Filter by company"),
    
    # Personal characteristics
    languages: Optional[List[str]] = Query(None, description="Languages spoken"),
    hobbies: Optional[List[str]] = Query(None, description="Hobbies"),
    personality_trait: Optional[str] = Query(None, description="Personality trait"),
    min_age: Optional[int] = Query(None, description="Minimum age"),
    max_age: Optional[int] = Query(None, description="Maximum age"),
    
    # Contact filters - NEW
    has_phone: Optional[bool] = Query(None, description="Filter users with phone numbers"),
    sms_enabled: Optional[bool] = Query(None, description="Filter users who can receive SMS"),
    phone_verified: Optional[bool] = Query(None, description="Filter users with verified phones"),
    country_code: Optional[str] = Query(None, description="Filter by phone country code (e.g., '+1')"),
    is_active: Optional[bool] = Query(None, description="Filter users who can receive SMS"),

    # General search
    name_contains: Optional[str] = Query(None, description="Search by name"),
    email_contains: Optional[str] = Query(None, description="Search by email"),
    tags: Optional[List[str]] = Query(None, description="Filter by tags"),
    
    # Pagination
    limit: int = Query(10, description="Number of results per page", ge=1, le=100),
    offset: int = Query(0, description="Number of results to skip", ge=0),
    
    # Sorting
    sort_by: str = Query("name", description="Field to sort by", regex="^(name|email|country|city|department|years_experience|age|created_at|phone)$"),
    sort_order: str = Query("asc", description="Sort order (asc or desc)", regex="^(asc|desc)$")
):
    """
    Search for users with various filters including phone number criteria
    """
    try:
        logger.info(f"User search initiated with filters: country={country}, department={department}, has_phone={has_phone}")
        
        searcher = PersonSearchEngine()
        results = await searcher.search_people(
            country=country,
            city=city,
            department=department,
            expertise_level=expertise_level,
            min_experience=min_experience,
            required_skills=required_skills,
            company=company,
            languages=languages,
            hobbies=hobbies,
            personality_trait=personality_trait,
            min_age=min_age,
            max_age=max_age,
            has_phone=has_phone,
            sms_enabled=sms_enabled,
            phone_verified=phone_verified,
            country_code=country_code,
            name_contains=name_contains,
            email_contains=email_contains,
            tags=tags,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        return results
        
    except Exception as e:
        logger.error(f"Search failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@user_router.get("/{user_id}/similar")
@limiter.limit("20/minute")
async def get_similar_users(
    request: Request,
    user_id: int,
    limit: int = Query(5, description="Number of similar users to return")
):
    """
    Find users similar to a given user
    """
    try:
        logger.info(f"Finding similar users for ID: {user_id}")
        
        searcher = PersonSearchEngine()
        similar_people = await searcher.find_similar_people(user_id, limit=limit)
        
        return {
            "person_id": user_id,
            "similar_people": similar_people,
            "count": len(similar_people)
        }
        
    except Exception as e:
        logger.error(f"Failed to find similar users: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to find similar users")

@user_router.get("/by-skill/{skill}")
@limiter.limit("30/minute")
async def get_users_by_skill(
    request: Request,
    skill: str,
    min_experience: Optional[int] = Query(None, description="Minimum years of experience"),
    limit: int = Query(10, description="Number of results")
):
    """
    Find users with a specific skill
    """
    try:
        logger.info(f"Finding users with skill: {skill}")
        
        searcher = PersonSearchEngine()
        results = await searcher.search_people(
            required_skills=[skill],
            min_experience=min_experience,
            limit=limit,
            sort_by="years_experience",
            sort_order="desc"
        )
        
        return results
        
    except Exception as e:
        logger.error(f"Failed to find users by skill: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to find users by skill")

@user_router.get("/location/{country}")
@limiter.limit("30/minute")
async def get_users_by_country(
    request: Request,
    country: str,
    city: Optional[str] = Query(None, description="Filter by city"),
    limit: int = Query(10, description="Number of results"),
    offset: int = Query(0, description="Number of results to skip")
):
    """
    Find users by location
    """
    try:
        logger.info(f"Finding users in country: {country}")
        
        searcher = PersonSearchEngine()
        results = await searcher.search_people(
            country=country,
            city=city,
            limit=limit,
            offset=offset
        )
        
        return results
        
    except Exception as e:
        logger.error(f"Failed to find users by location: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to find users by location")

@user_router.get("/department/{department}")
@limiter.limit("30/minute")
async def get_users_by_department(
    request: Request,
    department: Department,
    expertise_level: Optional[ExpertiseLevel] = Query(None, description="Filter by expertise level"),
    limit: int = Query(10, description="Number of results"),
    offset: int = Query(0, description="Number of results to skip")
):
    """
    Find users by department
    """
    try:
        logger.info(f"Finding users in department: {department}")
        
        searcher = PersonSearchEngine()
        results = await searcher.search_people(
            department=department,
            expertise_level=expertise_level,
            limit=limit,
            offset=offset
        )
        
        return results
        
    except Exception as e:
        logger.error(f"Failed to find users by department: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to find users by department")

@user_router.get("/health")
async def health_check():
    """Simple health check"""
    return {"status": "ok", "service": "users"}