from fastapi import APIRouter
from api.endpoints.sms  import sms_router

api_router = APIRouter()

api_router.include_router(sms_router, prefix="/v1")