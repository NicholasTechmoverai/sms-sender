# app/routes/webhook.py

from fastapi import APIRouter, Request, HTTPException, Header
from fastapi.responses import JSONResponse

from core.logger import setup_logger
from core.settings import settings
from utils.whatsapp_sender import meta_whatsapp_client

logger = setup_logger(__name__)
router = APIRouter(prefix="/webhook", tags=["webhook"])


@router.get("/whatsapp")
async def verify_webhook(
    hub_mode: str = Header(..., alias="hub.mode"),
    hub_verify_token: str = Header(..., alias="hub.verify_token"),
    hub_challenge: str = Header(..., alias="hub.challenge")
):
    """
    Verify webhook endpoint (GET request from Meta)
    """
    if hub_mode == "subscribe" and hub_verify_token == settings.META_VERIFY_TOKEN:
        logger.info("Webhook verified successfully")
        return JSONResponse(content=int(hub_challenge))
    else:
        logger.warning("Webhook verification failed")
        raise HTTPException(status_code=403, detail="Verification failed")


@router.post("/whatsapp")
async def handle_webhook(
    request: Request,
    x_hub_signature_256: Optional[str] = Header(None)
):
    """
    Handle incoming WhatsApp messages (POST request)
    """
    # Get raw body for signature verification
    body = await request.body()
    
    # Verify signature (optional but recommended)
    if x_hub_signature_256:
        is_valid = meta_whatsapp_client.verify_webhook_signature(
            request=request,
            payload=body,
            signature_header=x_hub_signature_256
        )
        
        if not is_valid:
            logger.warning("Invalid webhook signature")
            raise HTTPException(status_code=403, detail="Invalid signature")
    
    # Parse JSON payload
    payload = await request.json()
    
    # Process incoming messages
    messages = meta_whatsapp_client.parse_webhook_message(payload)
    
    for message in messages:
        logger.info(f"Received message from {message['from']}: {message}")
        
        # Handle different message types
        if message["type"] == "text":
            await handle_text_message(message)
        elif message["type"] == "interactive":
            await handle_interactive_message(message)
    
    # Always return 200 OK to acknowledge receipt
    return {"status": "ok"}


async def handle_text_message(message: dict):
    """
    Process incoming text messages
    """
    from_number = message["from"]
    text = message.get("text", "")
    
    logger.info(f"Processing text from {from_number}: {text}")
    
    # Example: Auto-reply if within 24h window
    if text.lower() == "help":
        await meta_whatsapp_client.send_text_message(
            to=from_number,
            text="How can I help you today?\n\n"
                 "1️⃣ Order Status\n"
                 "2️⃣ Support\n"
                 "3️⃣ Unsubscribe"
        )
    
    # You can trigger business logic here
    # e.g., update database, send to queue, etc.


async def handle_interactive_message(message: dict):
    """
    Process interactive messages (buttons, list replies)
    """
    interactive = message.get("interactive", {})
    interactive_type = interactive.get("type")
    
    if interactive_type == "button_reply":
        button_id = interactive.get("button_reply", {}).get("id")
        from_number = message["from"]
        
        logger.info(f"Button click from {from_number}: {button_id}")
        
        # Handle button actions
        if button_id == "order_status":
            await meta_whatsapp_client.send_text_message(
                to=from_number,
                text="Please enter your order number:"
            )