from fastapi import APIRouter, Request, HTTPException, Depends
from core.limiter import limiter
from core.logger import setup_logger
from utils.open_sms_sender import send_sms as send_sms_service, get_sms_balance
from schemas.sms import SMSRequest
from api.endpoints.auth import get_current_active_user

logger = setup_logger("sms")
sms_router = APIRouter()


@sms_router.get("/sms")
@limiter.limit("10/minute")
async def get_sms(request: Request, limit: str = 10, offset: str = 0, search: str = None, current_user = Depends(get_current_active_user)):
    try:
        logger.info("reading sms")
        return []
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@sms_router.post("/sms")
@limiter.limit("10/minute")
async def send_sms(request: Request, payload: SMSRequest, current_user = Depends(get_current_active_user)):
    try:
        res = await send_sms_service(
            recipient=",".join(payload.recipient),
            message=payload.message,
            type= payload.type,
            schedule_time=payload.schedule_time,
        )
        if not res.get("status") == "success":
            raise HTTPException(status_code=500, detail=res.get("message"))

        return res
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@sms_router.get("/sms/balance")
@limiter.limit("60/minute")
async def get_sms_balance_endpoint(request: Request, current_user = Depends(get_current_active_user)):
    try:
        logger.info("reading sms balance")
        bal = await get_sms_balance()
        return bal
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=str(e))