import json
import time,asyncio
import hmac
import hashlib
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta

import httpx
from fastapi import HTTPException, Request

from core.logger import setup_logger
from core.settings import settings

logger = setup_logger(__name__)


class MetaWhatsAppClient:
    """
    Direct Meta WhatsApp Cloud API client with async support
    """
    
    def __init__(self):
        """Initialize client using settings from core.settings"""
        self.api_version = settings.META_API_VERSION  # e.g., "v18.0"
        self.phone_number_id = settings.META_PHONE_NUMBER_ID
        self.access_token = settings.META_ACCESS_TOKEN
        self.app_secret = settings.META_APP_SECRET  # For webhook verification
        self.business_account_id = settings.META_BUSINESS_ACCOUNT_ID
        
        # Base URLs
        self.base_url = f"https://graph.facebook.com/{self.api_version}"
        self.messages_url = f"{self.base_url}/{self.phone_number_id}/messages"
        self.templates_url = f"{self.base_url}/{self.phone_number_id}/message_templates"
        
        # Rate limiting
        self.rate_limit_remaining = None
        self.rate_limit_reset = None
        
        # Message tracking
        self.message_log = []
        
        logger.info("Meta WhatsApp Client initialized")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests"""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
    
    async def send_template_message(
        self,
        to: str,
        template_name: str,
        language: str = "en",
        components: Optional[List[Dict]] = None,
        namespace: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send a pre-approved template message (required for first contact)
        
        Args:
            to: Recipient phone number (E.164 format, no +)
            template_name: Name of your approved template
            language: Language code (e.g., "en", "en_US")
            components: Template components (headers, body, buttons)
            namespace: Template namespace (optional, can be auto-discovered)
        
        Returns:
            API response with message ID
        
        Example components:
            components = [
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": "Alice"},
                        {"type": "text", "text": "10:00 AM"}
                    ]
                }
            ]
        """
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": language}
            }
        }
        
        if namespace:
            payload["template"]["namespace"] = namespace
        
        if components:
            payload["template"]["components"] = components
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.messages_url,
                    headers=self._get_headers(),
                    json=payload,
                    timeout=30.0
                )
                
                # Update rate limits from headers
                self.rate_limit_remaining = response.headers.get("x-app-usage-limit")
                self.rate_limit_reset = response.headers.get("x-app-usage-reset")
                
                if response.status_code == 200 or response.status_code == 201:
                    result = response.json()
                    logger.info(f"Template message sent to {to}: {result.get('messages', [{}])[0].get('id')}")
                    
                    # Log for tracking
                    self.message_log.append({
                        "to": to,
                        "type": "template",
                        "template_name": template_name,
                        "message_id": result.get('messages', [{}])[0].get('id'),
                        "timestamp": datetime.utcnow().isoformat()
                    })
                    
                    return result
                else:
                    error_data = response.json()
                    logger.error(f"Failed to send template: {error_data}")
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"WhatsApp API error: {error_data.get('error', {}).get('message', 'Unknown error')}"
                    )
                    
        except httpx.TimeoutException:
            logger.error("Timeout while sending WhatsApp message")
            raise HTTPException(status_code=504, detail="WhatsApp API timeout")
        except Exception as e:
            logger.error(f"Unexpected error sending WhatsApp message: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def send_text_message(
        self,
        to: str,
        text: str,
        preview_url: bool = False
    ) -> Dict[str, Any]:
        """
        Send a free-form text message (ONLY works within 24h window)
        
        Args:
            to: Recipient phone number (E.164 format, no +)
            text: Message text
            preview_url: Whether to show URL previews
        
        Returns:
            API response with message ID
        """
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "text",
            "text": {
                "preview_url": preview_url,
                "body": text
            }
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.messages_url,
                    headers=self._get_headers(),
                    json=payload,
                    timeout=30.0
                )
                
                if response.status_code == 200 or response.status_code == 201:
                    result = response.json()
                    logger.info(f"Text message sent to {to}")
                    
                    self.message_log.append({
                        "to": to,
                        "type": "text",
                        "message_id": result.get('messages', [{}])[0].get('id'),
                        "timestamp": datetime.utcnow().isoformat()
                    })
                    
                    return result
                else:
                    error_data = response.json()
                    logger.error(f"Failed to send text: {error_data}")
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"WhatsApp API error: {error_data.get('error', {}).get('message', 'Unknown error')}"
                    )
                    
        except Exception as e:
            logger.error(f"Error sending text message: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def send_bulk_templates(
        self,
        recipients: List[Dict[str, str]],
        template_name: str,
        template_variables: Dict[str, str],
        language: str = "en",
        batch_size: int = 50,
        delay_between_batches: int = 60
    ) -> Dict[str, Any]:
        """
        Send bulk template messages with rate limiting
        
        Args:
            recipients: List of dicts with 'phone' and any template variables
            template_name: Approved template name
            template_variables: Mapping of variable positions to field names
            language: Language code
            batch_size: Number of messages per batch
            delay_between_batches: Seconds to wait between batches
        
        Returns:
            Summary of results
        """
        total = len(recipients)
        results = {
            "total": total,
            "successful": 0,
            "failed": 0,
            "details": []
        }
        
        logger.info(f"Starting bulk send to {total} recipients using template '{template_name}'")
        
        for i in range(0, total, batch_size):
            batch = recipients[i:i+batch_size]
            batch_num = i // batch_size + 1
            total_batches = (total + batch_size - 1) // batch_size
            
            logger.info(f"Processing batch {batch_num}/{total_batches}")
            
            for recipient in batch:
                phone = recipient.get("phone")
                if not phone:
                    logger.warning(f"Skipping recipient without phone: {recipient}")
                    results["failed"] += 1
                    continue
                
                # Build components from variables
                components = []
                if template_variables:
                    body_params = []
                    for key, field in template_variables.items():
                        value = recipient.get(field, "")
                        if value:
                            body_params.append({"type": "text", "text": value})
                    
                    if body_params:
                        components.append({
                            "type": "body",
                            "parameters": body_params
                        })
                
                try:
                    response = await self.send_template_message(
                        to=phone,
                        template_name=template_name,
                        language=language,
                        components=components if components else None
                    )
                    
                    results["successful"] += 1
                    results["details"].append({
                        "phone": phone,
                        "status": "success",
                        "message_id": response.get('messages', [{}])[0].get('id')
                    })
                    
                except Exception as e:
                    logger.error(f"Failed to send to {phone}: {e}")
                    results["failed"] += 1
                    results["details"].append({
                        "phone": phone,
                        "status": "failed",
                        "error": str(e)
                    })
                
                # Small delay between individual messages
                await self._rate_limit_sleep(0.2)
            
            # Wait between batches
            if i + batch_size < total:
                logger.info(f"Waiting {delay_between_batches}s before next batch...")
                await self._rate_limit_sleep(delay_between_batches)
        
        logger.info(f"Bulk send complete: {results['successful']}/{total} successful")
        return results
    
    async def _rate_limit_sleep(self, seconds: float):
        """Helper to sleep without blocking the event loop"""
        await asyncio.sleep(seconds)
    
    async def get_template_list(self) -> List[Dict[str, Any]]:
        """Get all approved templates"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.templates_url,
                    headers=self._get_headers(),
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get("data", [])
                else:
                    logger.error(f"Failed to get templates: {response.text}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error fetching templates: {e}")
            return []
    
    async def get_message_status(self, message_id: str) -> Dict[str, Any]:
        """Get delivery status of a message"""
        try:
            url = f"{self.base_url}/{message_id}"
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    headers=self._get_headers(),
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"Failed to get message status: {response.text}")
                    return {}
                    
        except Exception as e:
            logger.error(f"Error fetching message status: {e}")
            return {}
    
    def verify_webhook_signature(
        self,
        request: Request,
        payload: bytes,
        signature_header: str
    ) -> bool:
        """
        Verify that webhook requests are from Meta
        
        Args:
            request: FastAPI request object
            payload: Raw request body
            signature_header: x-hub-signature-256 header value
        
        Returns:
            True if signature is valid
        """
        if not self.app_secret:
            logger.warning("No app secret configured, skipping webhook verification")
            return True
        
        try:
            # Compute expected signature
            expected_signature = hmac.new(
                self.app_secret.encode(),
                msg=payload,
                digestmod=hashlib.sha256
            ).hexdigest()
            
            # Compare with provided signature
            return hmac.compare_digest(
                signature_header,
                f"sha256={expected_signature}"
            )
            
        except Exception as e:
            logger.error(f"Error verifying webhook signature: {e}")
            return False
    
    def parse_webhook_message(self, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Parse incoming messages from webhook
        
        Returns:
            List of message objects with standardized format
        """
        messages = []
        
        try:
            # Webhook payload structure
            for entry in payload.get("entry", []):
                for change in entry.get("changes", []):
                    value = change.get("value", {})
                    
                    # Check for messages
                    for message in value.get("messages", []):
                        parsed = {
                            "id": message.get("id"),
                            "from": message.get("from"),
                            "timestamp": message.get("timestamp"),
                            "type": message.get("type"),
                            "text": None,
                            "interactive": None,
                            "context": message.get("context", {})
                        }
                        
                        # Extract message content
                        if message.get("type") == "text":
                            parsed["text"] = message.get("text", {}).get("body")
                        elif message.get("type") == "interactive":
                            parsed["interactive"] = message.get("interactive", {})
                        
                        messages.append(parsed)
            
            logger.info(f"Parsed {len(messages)} messages from webhook")
            return messages
            
        except Exception as e:
            logger.error(f"Error parsing webhook: {e}")
            return []


# Singleton instance for use across the app
meta_whatsapp_client = MetaWhatsAppClient()