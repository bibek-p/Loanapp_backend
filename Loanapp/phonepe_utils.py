import uuid
from phonepe.sdk.pg.payments.v1.models.request.pg_pay_request import PgPayRequest
from phonepe.sdk.pg.payments.v1.payment_client import PhonePePaymentClient
from phonepe.sdk.pg.env import Env
from django.conf import settings

def phonepe_create_order(ui_redirect_url, s2s_callback_url, unique_transaction_id, amount, user_id):
    """
    Create a PhonePe payment order
    """
    res = {}
    try:
        print(f"Initializing PhonePe client with: {settings.PHONEPE_MERCHANT_ID}")
        # Initialize PhonePe client
        phonepe_client = PhonePePaymentClient(
            settings.PHONEPE_MERCHANT_ID,
            settings.PHONEPE_SALT_KEY,
            settings.PHONEPE_SALT_INDEX,
            Env.PROD,  # environment
            True  # should_publish_events
        )
        

        # Convert amount to paise
        amount_in_paise = int(float(amount) * 100)

        print(f"Creating payment request for amount: {amount_in_paise} paise")
        # Create payment request
        pay_page_request = PgPayRequest.pay_page_pay_request_builder(
            merchant_transaction_id=unique_transaction_id,
            amount=amount_in_paise,
            merchant_user_id=str(user_id),
            callback_url="https://trendipay.digital/",
            redirect_url="https://trendipay.digital/"
        )

        # Make payment request
        pay_page_response = phonepe_client.pay(pay_page_request)
        print(f"PhonePe response: {pay_page_response}")
        
        if pay_page_response and hasattr(pay_page_response, 'data'):
            pay_page_url = pay_page_response.data.instrument_response.redirect_info.url
            res["status"] = True
            res["pay_page_url"] = pay_page_url
            # Convert response to dictionary
            res["response"] = {
                "success": pay_page_response.success,
                "code": pay_page_response.code,
                "message": pay_page_response.message,
                "data": {
                    "merchant_id": pay_page_response.data.merchant_id,
                    "merchant_transaction_id": pay_page_response.data.merchant_transaction_id,
                    "transaction_id": pay_page_response.data.transaction_id,
                    "instrument_response": {
                        "type": pay_page_response.data.instrument_response.type.value,
                        "redirect_info": {
                            "url": pay_page_response.data.instrument_response.redirect_info.url,
                            "method": pay_page_response.data.instrument_response.redirect_info.method
                        }
                    }
                }
            }
        else:
            raise Exception("Invalid response from PhonePe")

    except Exception as e:
        print(f"PhonePe payment error: {str(e)}")
        res["status"] = False
        res["error"] = str(e)

    return res 

def check_payment_status(merchant_transaction_id):
    """
    Check payment status from PhonePe API
    """
    res = {}
    try:
        # Initialize PhonePe client
        phonepe_client = PhonePePaymentClient(
            settings.PHONEPE_MERCHANT_ID,
            settings.PHONEPE_SALT_KEY,
            settings.PHONEPE_SALT_INDEX,
            Env.PROD,  # environment
            True  # should_publish_events
        )

        # Get status from PhonePe
        response = phonepe_client.check_status(merchant_transaction_id)
        print(f"PhonePe status response: {response}")  # Debug print
        
        if response.data:
            status = response.data.state
            if status == "COMPLETED":
                res["payment_status"] = "SUCCESS"
            else:
                res["payment_status"] = "FAILED"
        else:
            res["payment_status"] = "FAILED"

    except Exception as e:
        print(f"PhonePe status check error: {str(e)}")
        res["payment_status"] = "FAILED"

    return res 