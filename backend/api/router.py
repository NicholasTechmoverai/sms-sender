from fastapi import APIRouter
from api.endpoints.sms  import sms_router
from api.endpoints.users import user_router
from api.endpoints.auth import auth_router
from api.endpoints.data import data_router
from api.endpoints.whatsapp import router as whatsapp_router
api_router = APIRouter()

api_router.include_router(sms_router, prefix="/v1")
api_router.include_router(user_router, prefix="/v1")
api_router.include_router(auth_router, prefix="/v1")
api_router.include_router(data_router, prefix="/v1")
api_router.include_router(whatsapp_router, prefix="/v1")