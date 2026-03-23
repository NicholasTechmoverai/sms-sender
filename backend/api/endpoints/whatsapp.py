# app/routes/whatsapp.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from core.logger import setup_logger
from utils.whatsapp_sender import meta_whatsapp_client

logger = setup_logger(__name__)
router = APIRouter(prefix="/whatsapp", tags=["whatsapp"])


class TemplateMessageRequest(BaseModel):
    to: str
    template_name: str
    variables: Optional[dict] = None


class BulkTemplateRequest(BaseModel):
    recipients: List[dict]
    template_name: str
    template_variables: dict
    batch_size: int = 50


@router.post("/send-template")
async def send_template(request: TemplateMessageRequest):
    """
    Send a template message to a single recipient
    """
    try:
        # Build components from variables
        components = None
        if request.variables:
            body_params = []
            for key, value in request.variables.items():
                body_params.append({"type": "text", "text": str(value)})
            
            components = [{
                "type": "body",
                "parameters": body_params
            }]
        
        result = await meta_whatsapp_client.send_template_message(
            to=request.to,
            template_name=request.template_name,
            components=components
        )
        
        return {
            "success": True,
            "message_id": result.get("messages", [{}])[0].get("id"),
            "to": request.to
        }
        
    except Exception as e:
        logger.error(f"Failed to send template: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/send-bulk")
async def send_bulk(request: BulkTemplateRequest):
    """
    Send bulk template messages
    """
    try:
        results = await meta_whatsapp_client.send_bulk_templates(
            recipients=request.recipients,
            template_name=request.template_name,
            template_variables=request.template_variables,
            batch_size=request.batch_size
        )
        
        return results
        
    except Exception as e:
        logger.error(f"Failed to send bulk messages: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/templates")
async def list_templates():
    """
    List all approved templates
    """
    try:
        templates = await meta_whatsapp_client.get_template_list()
        return {"templates": templates}
        
    except Exception as e:
        logger.error(f"Failed to fetch templates: {e}")
        raise HTTPException(status_code=500, detail=str(e))