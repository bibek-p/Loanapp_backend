from django.conf import settings
import base64
import json
import hmac
import hashlib
import requests

class PhonePePaymentClient:
    def __init__(self):
        self.merchant_id = settings.PHONEPE_MERCHANT_ID
        self.salt_key = settings.PHONEPE_SALT_KEY
        self.api_url = settings.PHONEPE_API_URL

    def _generate_checksum(self, base64_payload):
        """Generate checksum for PhonePe request"""
        string = f"{base64_payload}/pg/v1/pay{self.salt_key}"
        return hmac.new(
            self.salt_key.encode(),
            string.encode(),
            hashlib.sha256
        ).hexdigest()

    def initiate_payment(self, payload):
        """
        Initiate payment with PhonePe
        """
        # Base64 encode the payload
        base64_payload = base64.b64encode(
            json.dumps(payload).encode()
        ).decode()

        # Calculate checksum
        checksum = self._generate_checksum(base64_payload)

        # Create request body
        request_body = {
            "request": base64_payload
        }

        # Set headers
        headers = {
            "Content-Type": "application/json",
            "X-VERIFY": f"{checksum}###1"
        }

        # Make API request
        response = requests.post(
            self.api_url,
            json=request_body,
            headers=headers
        )

        return response.json() if response.ok else None 