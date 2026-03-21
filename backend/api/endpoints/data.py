from fastapi import APIRouter, Request, HTTPException, Depends, Query
from typing import Optional, List
from core.logger import setup_logger
from core.limiter import limiter
from models.index import Person, Department, ExpertiseLevel
from schemas.auth import User as UserSchema
from api.endpoints.auth import get_current_active_user
from pydantic import BaseModel
from datetime import datetime

data_router = APIRouter(prefix="/data", tags=["Data Management"])
logger = setup_logger(__name__)


# Schemas for request/response
class PersonBase(BaseModel):
    name: str
    email: str
    age: Optional[int] = None
    birth_date: Optional[str] = None
    phone: Optional[str] = None
    country: str
    city: str
    address: Optional[str] = None
    postal_code: Optional[str] = None
    timezone: Optional[str] = None
    department: Department
    expertise_level: Optional[ExpertiseLevel] = None
    years_experience: int = 0
    skills: Optional[List[str]] = []
    current_position: Optional[str] = None
    company: Optional[str] = None
    languages: Optional[List[str]] = []
    bio: Optional[str] = None
    is_active: bool = True
    tags: Optional[List[str]] = []
    notes: Optional[str] = None
    sms_enabled: bool = True
    preferred_contact_method: str = "sms"

    class Config:
        from_attributes = True


class PersonCreate(PersonBase):
    pass


class PersonUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    age: Optional[int] = None
    phone: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    postal_code: Optional[str] = None
    timezone: Optional[str] = None
    department: Optional[Department] = None
    expertise_level: Optional[ExpertiseLevel] = None
    years_experience: Optional[int] = None
    skills: Optional[List[str]] = None
    current_position: Optional[str] = None
    company: Optional[str] = None
    languages: Optional[List[str]] = None
    bio: Optional[str] = None
    is_active: Optional[bool] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = None
    sms_enabled: Optional[bool] = None
    preferred_contact_method: Optional[str] = None

    class Config:
        from_attributes = True


# GET all people with pagination
@data_router.get("/people")
@limiter.limit("30/minute")
async def get_all_people(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    current_user=Depends(get_current_active_user),
):
    """Get all people with optional search and filtering"""
    try:
        query = Person.all()

        if search:
            # Search by name or email
            query = query.filter(
                Person.name.icontains(search) | Person.email.icontains(search)
            )

        if is_active is not None:
            query = query.filter(Person.is_active == is_active)

        total = await query.count()
        people = await query.offset(skip).limit(limit).all()

        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "items": [p.__dict__ for p in people],
        }
    except Exception as e:
        logger.error(f"Error fetching people: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error fetching people: {str(e)}")


# GET single person by ID
@data_router.get("/people/{person_id}")
@limiter.limit("30/minute")
async def get_person(
    request: Request, person_id: int, current_user=Depends(get_current_active_user)
):
    """Get a specific person by ID"""
    try:
        person = await Person.get_or_none(id=person_id)
        if not person:
            raise HTTPException(status_code=404, detail="Person not found")

        return person
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching person {person_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error fetching person: {str(e)}")


# POST create new person
@data_router.post("/people")
@limiter.limit("20/minute")
async def create_person(
    payload: PersonCreate,
    request: Request,
    current_user=Depends(get_current_active_user),
):
    """Create a new person"""
    try:
        # Check if email already exists
        existing = await Person.get_or_none(email=payload.email)
        if existing:
            raise HTTPException(status_code=400, detail="Email already exists")

        person = await Person.create(
            name=payload.name,
            email=payload.email,
            age=payload.age,
            birth_date=payload.birth_date,
            phone=payload.phone,
            country=payload.country,
            city=payload.city,
            address=payload.address,
            postal_code=payload.postal_code,
            timezone=payload.timezone,
            department=payload.department,
            expertise_level=payload.expertise_level,
            years_experience=payload.years_experience,
            skills=payload.skills,
            current_position=payload.current_position,
            company=payload.company,
            languages=payload.languages,
            bio=payload.bio,
            is_active=payload.is_active,
            tags=payload.tags,
            notes=payload.notes,
            sms_enabled=payload.sms_enabled,
            preferred_contact_method=payload.preferred_contact_method,
            form_number=f"FORM-{datetime.utcnow().timestamp()}",
        )

        logger.info(f"Created new person: {person.id} - {person.name}")
        return person
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating person: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error creating person: {str(e)}")


# PUT/PATCH update person
@data_router.put("/people/{person_id}")
@limiter.limit("20/minute")
async def update_person(
    person_id: int,
    payload: PersonUpdate,
    request: Request,
    current_user=Depends(get_current_active_user),
):
    """Update an existing person"""
    try:
        person = await Person.get_or_none(id=person_id)
        if not person:
            raise HTTPException(status_code=404, detail="Person not found")

        # Check if email is being changed and if it already exists
        if payload.email and payload.email != person.email:
            existing = await Person.get_or_none(email=payload.email)
            if existing:
                raise HTTPException(status_code=400, detail="Email already exists")

        update_data = payload.dict(exclude_unset=True)
        await person.update_from_dict(update_data).save()

        logger.info(f"Updated person: {person_id}")
        return person
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating person {person_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error updating person: {str(e)}")


# DELETE person
@data_router.delete("/people/{person_id}")
@limiter.limit("20/minute")
async def delete_person(
    person_id: int, request: Request, current_user=Depends(get_current_active_user)
):
    """Delete a person"""
    try:
        person = await Person.get_or_none(id=person_id)
        if not person:
            raise HTTPException(status_code=404, detail="Person not found")

        await person.delete()
        logger.info(f"Deleted person: {person_id}")
        return {"message": "Person deleted successfully", "id": person_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting person {person_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error deleting person: {str(e)}")


# GET list of available departments
@data_router.get("/departments")
@limiter.limit("30/minute")
async def get_departments(
    request: Request, current_user=Depends(get_current_active_user)
):
    """Get list of available departments"""
    return [
        {"value": dept.value, "label": dept.value.replace("_", " ").title()}
        for dept in Department
    ]


# GET list of available expertise levels
@data_router.get("/expertise-levels")
@limiter.limit("30/minute")
async def get_expertise_levels(
    request: Request, current_user=Depends(get_current_active_user)
):
    """Get list of available expertise levels"""
    return [
        {"value": level.value, "label": level.value.replace("_", " ").title()}
        for level in ExpertiseLevel
    ]
