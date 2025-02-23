import uuid
from phonepe.sdk.pg.payments.v1.models.request.pg_pay_request import PgPayRequest
from phonepe.sdk.pg.payments.v1.payment_client import PhonePePaymentClient
from phonepe.sdk.pg.env import Env
from django.conf import settings
import json, requests

def phonepe_create_order(ui_redirect_url, s2s_callback_url, unique_transaction_id, amount, user_id):
    """
    Create a PhonePe payment order
    """
    res = {}
    try:
        print(f"Initializing PhonePe client with: {settings.PHONEPE_MERCHANT_ID}")
        # Initialize PhonePe client
        phonepe_client = PhonePePaymentClient(
            "M222TOPSIPMSS",
            "7e3e9783-4852-4c4b-b186-8dcf19b307b1",
            1,
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


def UPI_PAYMENT(ui_redirect_url, s2s_callback_url, unique_transaction_id, amount, user_id):
    try :
        url = "https://allapi.in/order/create"

        payload = json.dumps({
        "token": "aede18-133815-c84254-5222f4-8e92a3",
        "order_id": str(unique_transaction_id),
        "txn_amount": amount,
        "txn_note": str(user_id),
        "product_name": "Redmi Note 12 Pro",
        "customer_name": "Adarsh Ranoji",
        "customer_mobile": "9999999999",
        "customer_email": "customer@gmail.com",
        "redirect_url": "https://trendipay.digital"
        })
        headers = {
        'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        final_response = {}
        if response.status_code == 200:
            data = json.loads(response.text)
            if data['status'] :
                final_response["status"] = True
                final_response["response"] = data['results']
                final_response["pay_page_url"] = data['results']['payment_url']
                return final_response
    except Exception as e:
        final_response={}
        final_response["status"] = False
        final_response["error"] = str(e)
        return final_response


def UPI_PAYMENT_status(merchant_transaction_id):
    try:
        url = "https://allapi.in/order/status"

        payload = json.dumps({
        "token": "aede18-133815-c84254-5222f4-8e92a3",
        "order_id": merchant_transaction_id
        })
        headers = {
        'Content-Type': 'application/json',
        'Cookie': 'PHPSESSID=d236c9387806a448d925798ff501b8d0'
        }
        final_response ={}
        response = requests.request("POST", url, headers=headers, data=payload)
        print(response.text)
        if response.status_code == 200:
            data = json.loads(response.text)
            if data['status'] :
                if data['results']['status'] == "Success":
                    final_response["payment_status"] = "SUCCESS"
                elif data['results']['status'] == "Pending":
                    final_response["payment_status"] = "PENDING"
                else:
                    final_response["payment_status"] = "FAILED"
                print(final_response)
                return final_response
        else:
            return {"status": False, "error": "Failed to fetch payment status"}


    
    except Exception as e:
        final_response={}
        final_response["status"] = False
        final_response["error"] = str(e)
        return final_response



