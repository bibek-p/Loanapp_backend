from rest_framework import viewsets
from .models import Loan, User, UserOTP, UserSession, HomeTopBanner, CreditCardCategory, CreditCard, Policy, LoanApplication, CheckoutConfig, Coupon, Payment, DeviceToken, Notification, NotificationTemplate, NotificationPreference, UserContacts
from .serializers import LoanSerializer, UserSerializer, UserOTPSerializer, UserSessionSerializer, OTPSerializer, HomeTopBannerSerializer, CreditCardCategorySerializer, CreditCardSerializer, PolicySerializer, LoanApplicationSerializer, CheckoutConfigSerializer, CouponSerializer, SaveContactsRequestSerializer, SaveContactsResponseSerializer
import random
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from django.utils import timezone
from datetime import timedelta
import secrets
from .decorators import validate_access_token
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404, render
from django.contrib import messages
from django.urls import reverse
from django.shortcuts import redirect
from .forms import CreditCardForm
from rest_framework.renderers import JSONRenderer
import uuid
import json
import requests,sys,os
from .phonepe_utils import *
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.db import transaction

class LoanViewSet(viewsets.ModelViewSet):
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class UserOTPViewSet(viewsets.ModelViewSet):
    queryset = UserOTP.objects.all()
    serializer_class = UserOTPSerializer

class UserSessionViewSet(viewsets.ModelViewSet):
    queryset = UserSession.objects.all()
    serializer_class = UserSessionSerializer


def send_otp_request_api(phone_number):
    url = "https://cpaas.messagecentral.com/auth/v1/authentication/token?customerId=C-58B94B38F8A045B&key=SGFudW1hbkA5ODdTUw==&scope=NEW&country=91&email=bibekispythondeveloper@gmail.com"

    payload={}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        access_token = response.json()['token']

        #  Sending OTP request
        url = "https://cpaas.messagecentral.com/verification/v3/send?countryCode=91&customerId=C-58B94B38F8A045B&flowType=SMS&mobileNumber="+str(phone_number)

        payload = {}
        headers = {
        'authToken': access_token
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        print(response.text)
        if response.status_code == 200:
            print("OTP sent successfully")
            verificationId =  response.json()['data']['verificationId']
            print(verificationId)
            return True,verificationId
        else:
            print("Failed to send OTP")
            return False,None


    else:
        return False,None
   

def send_otp_verify_api(otp,verificationId):
    url = "https://cpaas.messagecentral.com/auth/v1/authentication/token?customerId=C-58B94B38F8A045B&key=SGFudW1hbkA5ODdTUw==&scope=NEW&country=91&email=bibekispythondeveloper@gmail.com"

    payload={}
    headers = {}
    print(verificationId)
    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        access_token = response.json()['token']

        #  Sending OTP request
        url = "https://cpaas.messagecentral.com/verification/v3/validateOtp?&verificationId="+verificationId+"&code="+otp

        payload = {}
        headers = {
        'authToken': access_token
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        print(response.text)
        if response.status_code == 200:
            verificationStatus =  response.json()['data']['verificationStatus']
            if verificationStatus == "VERIFICATION_COMPLETED":
                return True
        else:
            return False


    else:
        return False
    


@api_view(['POST'])
@renderer_classes([JSONRenderer])
def register_or_login(request):
    phone_number = request.data.get('phone_number')
    
    # Check if user exists
    user, created = User.objects.get_or_create(phone_number=phone_number)
    
    # Mark any existing OTP as used
    UserOTP.objects.filter(phone_number=phone_number, is_used=False).update(is_used=True)
    
    # Generate a new 4-digit OTP
    # otp_code = str(random.randint(1000, 9999))  # Generate a 4-digit OTP
    send_otp_status,otp_code = send_otp_request_api(phone_number)
    if send_otp_status:

        expires_at = timezone.now() + timedelta(minutes=5)  # Set expiration time to 5 minutes from now
        UserOTP.objects.create(phone_number=phone_number, otp_code=otp_code, is_used=False, expires_at=expires_at)
        
        # Here you would send the OTP to the user's phone number via SMS
        print(f"OTP for {phone_number}: {otp_code}")  # Replace this with actual SMS sending logic
    
        return Response({"message": "OTP sent to your phone number."}, status=status.HTTP_200_OK)
    else:
        return Response({"error": "Failed to send OTP to your phone number."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

@api_view(['POST'])
@renderer_classes([JSONRenderer])
def verify_otp(request):
    serializer = OTPSerializer(data=request.data)
    if serializer.is_valid():
        phone_number = serializer.validated_data['phone_number']
        otp_code = serializer.validated_data['otp_code']
        print(phone_number, otp_code)
        
        try:
            otp_entry = UserOTP.objects.filter(phone_number=phone_number).order_by('-created_at').first()
            print(otp_entry)
            verificationId = otp_entry.otp_code
            verify_status = send_otp_verify_api(otp_code,verificationId)
            if verify_status == True:

            
                # # Check if the OTP has expired
                # if otp_entry.expires_at < timezone.now():
                #     return Response({"error": "OTP has expired."}, status=status.HTTP_400_BAD_REQUEST)
                
                user = User.objects.get(phone_number=phone_number)
                
                # Mark OTP as used
                otp_entry.is_used = True
                otp_entry.save()
                
                # Update user verification status
                user.is_verified = True
                user.save()
                
                # Generate an access token
                access_token = AccessToken.for_user(user)
                
                return Response({"message": "OTP verified successfully.", "access_token": str(access_token)}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)
        except UserOTP.DoesNotExist:
            return Response({"error": "Invalid or expired OTP."}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@renderer_classes([JSONRenderer])
def resend_otp(request):
    phone_number = request.data.get('phone_number')
    
    # Check if user exists
    try:
        user = User.objects.get(phone_number=phone_number)
        
        # Mark any existing OTP as used
        UserOTP.objects.filter(phone_number=phone_number, is_used=False).update(is_used=True)
        
        # Generate a new 4-digit OTP
        # otp_code = str(random.randint(1000, 9999))  # Generate a 4-digit OTP
        send_otp_status,otp_code = send_otp_request_api(phone_number)
        if send_otp_status:
            expires_at = timezone.now() + timedelta(minutes=5)  # Set expiration time to 5 minutes from now
            UserOTP.objects.create(phone_number=phone_number, otp_code=otp_code, is_used=False, expires_at=expires_at)
            
            # Here you would send the OTP to the user's phone number via SMS
            print(f"Resent OTP for {phone_number}: {otp_code}")  # Replace this with actual SMS sending logic
            
            return Response({"message": "OTP resent to your phone number."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Failed to send OTP to your phone number."}, status=status.HTTP_404_NOT_FOUND)

    except User.DoesNotExist:
        return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@renderer_classes([JSONRenderer])
def some_protected_view(request):
    return Response({"message": "This is a protected view."}, status=status.HTTP_200_OK)

@api_view(['GET'])
@renderer_classes([JSONRenderer])
def get_live_banners(request):
    # Retrieve all live banners
    live_banners = HomeTopBanner.objects.filter(is_live=True)
    serializer = HomeTopBannerSerializer(live_banners, many=True)
    
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
@renderer_classes([JSONRenderer])
def add_banner(request):
    serializer = HomeTopBannerSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()  # Save the new banner to the database
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@renderer_classes([JSONRenderer])
def delete_banner(request, banner_id):
    try:
        banner = HomeTopBanner.objects.get(id=banner_id)
        banner.delete()  # Delete the banner
        return Response({"message": "Banner deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
    except HomeTopBanner.DoesNotExist:
        return Response({"error": "Banner not found."}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def add_credit_card_category(request):
    serializer = CreditCardCategorySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()  # Save the new category to the database
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_credit_card_categories(request):
    categories = CreditCardCategory.objects.all()
    serializer = CreditCardCategorySerializer(categories, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['PUT'])
def update_credit_card_category(request, category_id):
    try:
        category = CreditCardCategory.objects.get(id=category_id)
    except CreditCardCategory.DoesNotExist:
        return Response({"error": "Category not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = CreditCardCategorySerializer(category, data=request.data)
    if serializer.is_valid():
        serializer.save()  # Update the category
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def delete_credit_card_category(request, category_id):
    try:
        category = CreditCardCategory.objects.get(id=category_id)
        category.delete()  # Delete the category
        return Response({"message": "Category deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
    except CreditCardCategory.DoesNotExist:
        return Response({"error": "Category not found."}, status=status.HTTP_404_NOT_FOUND)

def get_credit_cards(request):
    credit_cards = CreditCard.objects.all()
    return render(request, 'credit_cards/list.html', {'credit_cards': credit_cards})

def add_credit_card(request):
    if request.method == 'POST':
        form = CreditCardForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Credit card created successfully.')
            return redirect('get_credit_cards')
    else:
        form = CreditCardForm()
    return render(request, 'credit_cards/form.html', {'form': form})

def update_credit_card(request, card_id):
    credit_card = get_object_or_404(CreditCard, id=card_id)
    if request.method == 'POST':
        form = CreditCardForm(request.POST, instance=credit_card)
        if form.is_valid():
            form.save()
            messages.success(request, 'Credit card updated successfully.')
            return redirect('get_credit_cards')
    else:
        form = CreditCardForm(instance=credit_card)
    return render(request, 'credit_cards/form.html', {'form': form})

def delete_credit_card(request, card_id):
    credit_card = get_object_or_404(CreditCard, id=card_id)
    if request.method == 'POST':
        credit_card.delete()
        messages.success(request, 'Credit card deleted successfully.')
    return redirect('get_credit_cards')

@api_view(['POST'])
@renderer_classes([JSONRenderer])
def create_loan_application(request):
    """Create a new loan application"""
    data = request.data.copy()
    
    # Get user by phone number
    try:
        phone_number = data.get('userId')  # Get phone number from request
        user = User.objects.get(phone_number=phone_number)
        data['user'] = user.id  # Set the user ID in the data
    except User.DoesNotExist:
        return Response(
            {"error": "User not found with provided phone number"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    data['status'] = 'draft'
    
    print("Request Data:", data)  # Debug print
    serializer = LoanApplicationSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    print("Serializer Errors:", serializer.errors)  # Debug print
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@renderer_classes([JSONRenderer])
def update_loan_application(request, application_id):
    """Update an existing loan application"""
    loan_application = get_object_or_404(
        LoanApplication, 
        id=application_id
    )
    
    # Get the current data
    current_data = LoanApplicationSerializer(loan_application).data
    
    # Update only the fields that are present in the request
    update_data = request.data.copy()
    
    # Remove undefined fields
    fields_to_update = ['current_step', 'loan_details', 'personal_info', 'kyc_info', 'professional_info']
    for field in fields_to_update:
        if field in update_data and (update_data[field] == 'undefined' or update_data[field] is None):
            del update_data[field]
        elif field not in update_data:
            # Keep existing data for fields not in the request
            if field in current_data:
                update_data[field] = current_data[field]
    
    print("Update Data:", update_data)  # Debug print to see what's being sent to serializer
    
    serializer = LoanApplicationSerializer(
        loan_application, 
        data=update_data,
        partial=True
    )
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    print("Serializer Errors:", serializer.errors)  # Debug print
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@renderer_classes([JSONRenderer])
def get_loan_application(request, application_id):
    """Get a specific loan application"""
    phone_number = request.GET.get('userId')
    try:
        user = User.objects.get(phone_number=phone_number)
    except User.DoesNotExist:
        return Response(
            {"error": "User not found with provided phone number"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    loan_application = get_object_or_404(
        LoanApplication, 
        id=application_id, 
        user=user
    )
    serializer = LoanApplicationSerializer(loan_application)
    return Response(serializer.data)

@api_view(['GET'])
@renderer_classes([JSONRenderer])
def get_user_applications(request):
    """Get all loan applications for a user"""
    phone_number = request.GET.get('userId')
    try:
        user = User.objects.get(phone_number=phone_number)
    except User.DoesNotExist:
        return Response(
            {"error": "User not found with provided phone number"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    applications = LoanApplication.objects.filter(user=user)
    serializer = LoanApplicationSerializer(applications, many=True)
    return Response({'applications': serializer.data})

@api_view(['POST'])
@renderer_classes([JSONRenderer])
def submit_application(request, application_id):
    """Submit a completed loan application"""
    phone_number = request.data.get('userId')
    try:
        user = User.objects.get(phone_number=phone_number)
    except User.DoesNotExist:
        return Response(
            {"error": "User not found with provided phone number"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    loan_application = get_object_or_404(
        LoanApplication, 
        id=application_id, 
        user=user
    )
    
    # Validate all required fields are present
    if not all([
        loan_application.loan_details,
        loan_application.personal_info,
        loan_application.kyc_info,
        loan_application.professional_info
    ]):
        return Response(
            {'error': 'All sections must be completed before submission'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    loan_application.status = 'submitted'
    loan_application.save()
    
    serializer = LoanApplicationSerializer(loan_application)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
@renderer_classes([JSONRenderer])
def credit_card_list_api(request):
    """
    API endpoint to get list of credit cards
    GET: Returns list of all active credit cards with optional filters
    """
    try:
        # Get query parameters
        category = request.GET.get('category')
        bank = request.GET.get('bank')
        min_fee = request.GET.get('min_fee')
        max_fee = request.GET.get('max_fee')

        # Start with all active cards
        queryset = CreditCard.objects.filter(active_status=True)

        # Apply filters if provided
        if category:
            queryset = queryset.filter(category__id=category)

        if bank:
            queryset = queryset.filter(bank_name__icontains=bank)

        if min_fee:
            queryset = queryset.filter(annual_fee__gte=float(min_fee))

        if max_fee:
            queryset = queryset.filter(annual_fee__lte=float(max_fee))

        # Order by card name
        queryset = queryset.order_by('card_name')

        # Serialize the data
        serializer = CreditCardSerializer(queryset, many=True)

        return Response({
            'status': 'success',
            'message': 'Credit cards retrieved successfully',
            'count': queryset.count(),
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
@renderer_classes([JSONRenderer])
def credit_card_category_list_api(request):
    """
    API endpoint to get list of credit card categories
    GET: Returns list of all credit card categories
    """
    try:
        # Get query parameters
        search = request.GET.get('search', '')

        # Start with all categories
        queryset = CreditCardCategory.objects.all()

        # Apply search filter if provided
        if search:
            queryset = queryset.filter(name__icontains=search)

        # Order by name
        queryset = queryset.order_by('name')

        # Get card count for each category
        categories_with_count = []
        for category in queryset:
            category_data = CreditCardCategorySerializer(category).data
            category_data['card_count'] = category.credit_cards.filter(active_status=True).count()
            categories_with_count.append(category_data)

        return Response({
            'status': 'success',
            'message': 'Categories retrieved successfully',
            'count': len(categories_with_count),
            'data': categories_with_count
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@renderer_classes([JSONRenderer])
def get_checkout_config(request):
    """
    Get all checkout configurations
    """
    try:
        configs = CheckoutConfig.objects.all()
        serializer = CheckoutConfigSerializer(configs, many=True)
        
        return Response({
            'status': 'success',
            'message': 'Checkout configurations retrieved successfully',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@renderer_classes([JSONRenderer])
def get_live_coupons(request):
    """
    Get all live coupons
    """
    try:
        coupons = Coupon.objects.filter(is_live_to_list=True)
        serializer = CouponSerializer(coupons, many=True)
        
        return Response({
            'status': 'success',
            'message': 'Live coupons retrieved successfully',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@renderer_classes([JSONRenderer])
def validate_coupon(request):
    """
    Validate a coupon code
    """
    try:
        coupon_code = request.data.get('coupon_code')
        
        if not coupon_code:
            return Response({
                'status': 'error',
                'message': 'Coupon code is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            coupon = Coupon.objects.get(
                coupon_code=coupon_code,
                is_live_to_list=True
            )
            serializer = CouponSerializer(coupon)
            
            return Response({
                'status': 'success',
                'message': 'Valid coupon code',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Coupon.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Invalid or inactive coupon code'
            }, status=status.HTTP_404_NOT_FOUND)
    
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@renderer_classes([JSONRenderer])
def initiate_phonepe_payment(request):
    """
    Initiate a PhonePe payment
    """
    try:
        print(request.data)
        # Get request data
        amount = request.data.get('amount')
        application_id = request.data.get('applicationId')
        gateway = request.data.get('gateway')

        # Validate input
        if not all([amount, application_id, gateway]):
            return Response({
                'status': 'error',
                'message': 'Missing required fields'
            }, status=status.HTTP_400_BAD_REQUEST)

        if gateway != 'phonepe':
            return Response({
                'status': 'error',
                'message': 'Invalid payment gateway'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get loan application and user details
        try:
            loan_application = LoanApplication.objects.get(id=application_id)
            user = loan_application.user
        except LoanApplication.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Invalid application ID'
            }, status=status.HTTP_404_NOT_FOUND)

        # Create unique transaction ID
        merchant_transaction_id = f"MT{uuid.uuid4().hex[:16].upper()}"

        # Get callback URLs
        ui_redirect_url = request.build_absolute_uri(reverse('payment_redirect'))
        s2s_callback_url = request.build_absolute_uri(reverse('payment_callback'))

        # Create PhonePe order
        payment_response = UPI_PAYMENT(
            ui_redirect_url=ui_redirect_url,
            s2s_callback_url=s2s_callback_url,
            unique_transaction_id=merchant_transaction_id,
            amount=float(amount),
            user_id=user.id
        )

        if payment_response["status"]:
            # Save payment details
            gateway_response = payment_response.get("response", {})
            
            # Convert Decimal to float for JSON serialization
            amount = float(amount)
            
            payment = Payment.objects.create(
                user=user,
                application=loan_application,
                amount=amount,
                transaction_id=merchant_transaction_id,
                gateway='phonepe',
                status='initiated',
                gateway_response=dict(gateway_response)  # Ensure it's a dict
            )

            return Response({
                'status': 'success',
                'message': 'Payment initiated successfully',
                'data': {
                    'payment_id': payment.id,
                    'transaction_id': merchant_transaction_id,
                    'redirect_url': payment_response["pay_page_url"]
                }
            }, status=status.HTTP_200_OK)
        
        

        return Response({
            'status': 'error',
            'message': 'Failed to initiate payment',
            'details': payment_response.get("error", "Payment initiation failed")
        }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@renderer_classes([JSONRenderer])
def payment_callback(request):
    """
    Server-to-server callback for PhonePe payments
    """
    try:
        # Get callback data
        callback_data = request.data
        transaction_id = callback_data.get('merchantTransactionId')

        # Get payment record
        try:
            payment = Payment.objects.get(transaction_id=transaction_id)
        except Payment.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Payment not found'
            }, status=status.HTTP_404_NOT_FOUND)

        # Update payment status based on callback
        payment_status = callback_data.get('code')
        if payment_status == 'PAYMENT_SUCCESS':
            payment.status = 'completed'
        elif payment_status == 'PAYMENT_ERROR' or payment_status == 'PAYMENT_DECLINED':
            payment.status = 'failed'
        else:
            payment.status = 'pending'

        payment.gateway_response = callback_data
        payment.save()

        return Response({
            'status': 'success',
            'message': 'Callback processed successfully'
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET', 'POST'])
@renderer_classes([JSONRenderer])
def payment_redirect(request):
    """
    Client-side redirect for PhonePe payments
    """
    try:
        # Get transaction details from request
        transaction_id = request.GET.get('merchantTransactionId') or request.POST.get('merchantTransactionId')
        
        if not transaction_id:
            return Response({
                'status': 'error',
                'message': 'Transaction ID not found'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get payment record
        try:
            payment = Payment.objects.get(transaction_id=transaction_id)
        except Payment.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Payment not found'
            }, status=status.HTTP_404_NOT_FOUND)

        # Return payment status
        return Response({
            'status': 'success',
            'message': 'Payment status retrieved',
            'data': {
                'payment_id': payment.id,
                'transaction_id': payment.transaction_id,
                'status': payment.status,
                'amount': payment.amount
            }
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@renderer_classes([JSONRenderer])
def verify_payment(request):
    """
    Verify payment status from PhonePe
    """
    try:
        # Get order ID from request
        order_id = request.data.get('orderId')
        
        if not order_id:
            return Response({
                'status': 'error',
                'message': 'Order ID is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get payment record
        try:
            payment = Payment.objects.get(transaction_id=order_id)
        except Payment.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Payment not found'
            }, status=status.HTTP_404_NOT_FOUND)

        # Check status from PhonePe
        status_response = UPI_PAYMENT_status(order_id)
        print(f"Status response: {status_response}")  # Debug print
        
        # Update payment status in DB
        payment.status = 'completed' if status_response["payment_status"] == "SUCCESS" else 'failed'
        if status_response["payment_status"] == "SUCCESS":
            payment.status = 'completed'
        elif status_response["payment_status"] == "PENDING":
            payment.status = 'pending'
        else:
            payment.status = 'failed'
        payment.gateway_response = status_response
        payment.save()

        # Return response
        response_data = {
            'status': 'success',
            'message': 'Payment status retrieved',
            'data': {
                'payment_id': str(payment.id),
                'transaction_id': payment.transaction_id,
                'amount': float(payment.amount),
                'payment_status': payment.status,
                'created_at': payment.created_at.isoformat(),
                'updated_at': payment.updated_at.isoformat()
            }
        }

        # Add status-specific messages
        if payment.status == 'completed':
            response_data['data']['message'] = 'Payment successful'
        elif payment.status == 'failed':
            response_data['data']['message'] = 'Payment failed'
        else:
            response_data['data']['message'] = 'Payment is being processed'

        return Response(response_data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@renderer_classes([JSONRenderer])
def list_user_loan_applications(request):
    """
    Get list of loan applications for a user by phone number
    """
    try:
        # Get phone number from request
        phone_number = request.data.get('phone_number')
        
        if not phone_number:
            return Response({
                'status': 'error',
                'message': 'Phone number is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get user by phone number
        try:
            user = User.objects.get(phone_number=phone_number)
        except User.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)

        # Get all loan applications for the user
        loan_applications = LoanApplication.objects.filter(user=user).order_by('-created_at')
        
        # Get associated payments for each application
        applications_data = []
        for application in loan_applications:
            # Get latest payment for this application
            latest_payment = Payment.objects.filter(
                application=application
            ).order_by('-created_at').first()
            
            application_data = LoanApplicationSerializer(application).data
            application_data['payment_status'] = latest_payment.status if latest_payment else None
            application_data['payment_amount'] = float(latest_payment.amount) if latest_payment else None
            application_data['payment_date'] = latest_payment.created_at if latest_payment else None
            
            applications_data.append(application_data)

        return Response({
            'status': 'success',
            'message': 'Loan applications retrieved successfully',
            'data': {
                'applications': applications_data
            }
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@renderer_classes([JSONRenderer])
def get_loan_application_details(request):
    """
    Get detailed information about a specific loan application
    """
    try:
        # Get application ID from request
        application_id = request.data.get('application_id')
        
        if not application_id:
            return Response({
                'status': 'error',
                'message': 'Application ID is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get loan application
        try:
            loan_application = LoanApplication.objects.get(id=application_id)
        except LoanApplication.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Loan application not found'
            }, status=status.HTTP_404_NOT_FOUND)

        # Get latest payment for this application
        latest_payment = Payment.objects.filter(
            application=loan_application
        ).order_by('-created_at').first()

        # Serialize application data
        application_data = LoanApplicationSerializer(loan_application).data
        
        # Add payment information and message
        application_data.update({
            'payment_info': {
                'status': latest_payment.status if latest_payment else None,
                'amount': float(latest_payment.amount) if latest_payment else None,
                'transaction_id': latest_payment.transaction_id if latest_payment else None,
                'payment_date': latest_payment.created_at if latest_payment else None,
                'gateway': latest_payment.gateway if latest_payment else None
            },
            'message': loan_application.message
        })

        return Response({
            'status': 'success',
            'message': 'Application details retrieved successfully',
            'data': application_data
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@renderer_classes([JSONRenderer])
def get_policy_by_title(request):
    """
    Get policy details by title
    """
    try:
        title = request.GET.get('title', '').lower()
        
        if not title:
            return Response({
                'status': 'error',
                'message': 'Title parameter is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            policy = Policy.objects.get(title__iexact=title, is_active=True)
        except Policy.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Policy not found'
            }, status=status.HTTP_404_NOT_FOUND)

        return Response({
            'status': 'success',
            'message': 'Policy retrieved successfully',
            'data': {
                'title': policy.title,
                'content': policy.content,
                'created_at': policy.created_at,
                'updated_at': policy.updated_at
            }
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@renderer_classes([JSONRenderer])
def register_device(request):
    """
    Register a device for push notifications
    """
    try:
        user = request.user
        device_token = request.data.get('device_token')
        device_type = request.data.get('device_type')
        print(request.data)

        if not all([device_token, device_type]):
            return Response({
                'status': 'error',
                'message': 'Device token and type are required'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Create or update device token
        device, created = DeviceToken.objects.update_or_create(
            user=user,
            device_token=device_token,
            defaults={
                'device_type': device_type,
                'is_active': True
            }
        )

        return Response({
            'status': 'success',
            'message': 'Device registered successfully',
            'data': {
                'device_id': device.id,
                'is_active': device.is_active
            }
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@renderer_classes([JSONRenderer])
def list_notifications(request):
    """
    Get list of notifications for a user
    """
    try:
        # Get query parameters
        notification_type = request.GET.get('type', 'all')
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 10))

        # Get notifications
        notifications = Notification.objects.filter(user=request.user)

        # Apply type filter
        if notification_type != 'all':
            notifications = notifications.filter(type=notification_type)

        # Order by date
        notifications = notifications.order_by('-created_at')

        # Paginate results
        paginator = Paginator(notifications, page_size)
        notifications_page = paginator.get_page(page)

        # Serialize data
        data = [{
            'id': str(notif.id),
            'title': notif.title,
            'body': notif.body,
            'type': notif.type,
            'is_read': notif.is_read,
            'metadata': notif.metadata,
            'deep_link': notif.deep_link,
            'created_at': notif.created_at
        } for notif in notifications_page]

        return Response({
            'status': 'success',
            'message': 'Notifications retrieved successfully',
            'data': {
                'notifications': data,
                'total_count': paginator.count,
                'total_pages': paginator.num_pages,
                'current_page': page,
                'has_next': notifications_page.has_next(),
                'has_previous': notifications_page.has_previous()
            }
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@renderer_classes([JSONRenderer])
def mark_notifications_read(request):
    """
    Mark notifications as read
    """
    try:
        notification_ids = request.data.get('notification_ids', [])
        mark_all = request.data.get('mark_all', False)
        notification_type = request.data.get('type')

        notifications = Notification.objects.filter(user=request.user)

        if mark_all:
            # Mark all notifications as read
            if notification_type:
                notifications = notifications.filter(type=notification_type)
            notifications.update(is_read=True)
        elif notification_ids:
            # Mark specific notifications as read
            notifications.filter(id__in=notification_ids).update(is_read=True)
        else:
            return Response({
                'status': 'error',
                'message': 'Please provide notification IDs or set mark_all to true'
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            'status': 'success',
            'message': 'Notifications marked as read successfully'
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@renderer_classes([JSONRenderer])
def send_notification(request):
    """
    Send notification to users (Admin only)
    """
    try:
        if not request.user.is_staff:
            return Response({
                'status': 'error',
                'message': 'Only admin users can send notifications'
            }, status=status.HTTP_403_FORBIDDEN)

        title = request.data.get('title')
        body = request.data.get('body')
        notification_type = request.data.get('type')
        user_ids = request.data.get('user_ids', [])
        send_to_all = request.data.get('send_to_all', False)
        schedule_time = request.data.get('schedule_time')
        deep_link = request.data.get('deep_link')
        metadata = request.data.get('metadata', {})

        if not all([title, body, notification_type]):
            return Response({
                'status': 'error',
                'message': 'Title, body and type are required'
            }, status=status.HTTP_400_BAD_REQUEST)

        notifications = []
        users = User.objects.all() if send_to_all else User.objects.filter(id__in=user_ids)

        for user in users:
            notification = Notification.objects.create(
                user=user,
                title=title,
                body=body,
                type=notification_type,
                deep_link=deep_link,
                metadata=metadata,
                expires_at=schedule_time
            )
            notifications.append(notification)

            # Get user's device tokens
            device_tokens = DeviceToken.objects.filter(user=user, is_active=True)
            
            # Here you would integrate with FCM/APNS to send push notifications
            # This is a placeholder for actual push notification logic
            for device in device_tokens:
                print(f"Sending push notification to device {device.device_token}")

        return Response({
            'status': 'success',
            'message': f'Notification sent to {len(notifications)} users',
            'data': {
                'notification_count': len(notifications)
            }
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET', 'PUT'])
@renderer_classes([JSONRenderer])
def notification_settings(request):
    """
    Get or update notification preferences
    """
    try:
        preference, created = NotificationPreference.objects.get_or_create(user=request.user)

        if request.method == 'GET':
            return Response({
                'status': 'success',
                'message': 'Notification preferences retrieved successfully',
                'data': {
                    'personal_notifications': preference.personal_notifications,
                    'loan_notifications': preference.loan_notifications,
                    'payment_notifications': preference.payment_notifications,
                    'quiet_hours_start': preference.quiet_hours_start,
                    'quiet_hours_end': preference.quiet_hours_end
                }
            }, status=status.HTTP_200_OK)

        # Update preferences
        preference.personal_notifications = request.data.get(
            'personal_notifications', preference.personal_notifications)
        preference.loan_notifications = request.data.get(
            'loan_notifications', preference.loan_notifications)
        preference.payment_notifications = request.data.get(
            'payment_notifications', preference.payment_notifications)
        preference.quiet_hours_start = request.data.get(
            'quiet_hours_start', preference.quiet_hours_start)
        preference.quiet_hours_end = request.data.get(
            'quiet_hours_end', preference.quiet_hours_end)
        preference.save()

        return Response({
            'status': 'success',
            'message': 'Notification preferences updated successfully'
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def landing_page(request):
    """
    Landing page view for Trendipay educational platform
    """
    courses = [
        {
            'id': 1,
            'title': 'Machine Learning Fundamentals',
            'description': 'Learn the basics of Machine Learning with Python',
            'price': 4999,
            'duration': '3 months',
            'image_url': '/static/images/courses/ml-fundamentals.jpg',
            'features': [
                'Python Programming Basics',
                'Data Preprocessing',
                'Supervised Learning',
                'Model Evaluation'
            ]
        },
        {
            'id': 2,
            'title': 'Deep Learning Specialization',
            'description': 'Master Deep Learning and Neural Networks',
            'price': 7999,
            'duration': '4 months',
            'image_url': '/static/images/courses/deep-learning.jpg',
            'features': [
                'Neural Networks',
                'Computer Vision',
                'Natural Language Processing',
                'Project Implementation'
            ]
        },
        {
            'id': 3,
            'title': 'AI for Business Analytics',
            'description': 'Apply AI to solve real business problems',
            'price': 5999,
            'duration': '3 months',
            'image_url': '/static/images/courses/ai-business.jpg',
            'features': [
                'Business Intelligence',
                'Predictive Analytics',
                'Data Visualization',
                'Decision Making'
            ]
        }
    ]
    
    return render(request, 'landing/home.html', {
        'courses': courses
    }) 

def about_us(request):
     return render(request, 'landing/aboutus.html') 

def pages(request,page):
    res={}
    if page == "terms":
        res = {
            'title': 'Terms & Conditions',
            'content': ''' 
            
            <p>Welcome to Trendipay! By accessing or using our website and services, you agree to comply with and be bound by the following Terms and Conditions. Please read them carefully before using our platform. If you do not agree with these terms, you must refrain from using Trendipay.</p>
                <hr>
                <h3><strong>1. Introduction</strong></h3>
                <p>Trendipay offers courses and educational materials for individuals seeking to enhance their knowledge and skills. These Terms and Conditions govern your use of our platform, including purchases, access, and usage of courses.</p>
                <hr>
                <h3><strong>2. Eligibility</strong></h3>
                <p>By using Trendipay, you represent and warrant that you:</p>
                <ul>
                    <li>Are at least 18 years old or have parental/guardian consent if under 18.</li>
                    <li>Have the legal capacity to enter into these Terms and Conditions.</li>
                </ul>
                <hr>
                <h3><strong>3. Account Registration</strong></h3>
                <ul>
                    <li>To access our courses, you may be required to create an account.</li>
                    <li>You are responsible for maintaining the confidentiality of your account credentials.</li>
                    <li>You agree to provide accurate and complete information during registration.</li>
                    <li>Trendipay reserves the right to suspend or terminate accounts for any breach of these terms.</li>
                </ul>
                <hr>
                <h3><strong>4. Purchases and Payments</strong></h3>
                <ul>
                    <li>All prices for courses are displayed in [currency] and are subject to change without notice.</li>
                    <li>Payments must be completed via the methods provided on our platform.</li>
                    <li>Trendipay reserves the right to decline or cancel any purchase for any reason.</li>
                    <li>Taxes and additional fees may apply based on your location.</li>
                </ul>
                <hr>
                <h3><strong>5. Refund Policy</strong></h3>
                <ul>
                    <li>Refund requests must be submitted within [insert time frame, e.g., 7 days] of purchase.</li>
                    <li>Refunds are subject to our approval and may be denied if course content has been accessed or downloaded.</li>
                    <li>Processing times for refunds may vary depending on the payment method.</li>
                </ul>
                <hr>
                <h3><strong>6. Use of Content</strong></h3>
                <ul>
                    <li>All course materials, including videos, documents, and other resources, are the intellectual property of Trendipay.</li>
                    <li>You are granted a limited, non-exclusive, non-transferable license to access and use the materials for personal, non-commercial purposes.</li>
                    <li>You may not reproduce, distribute, or share any course content without our explicit written permission.</li>
                </ul>
                <hr>
                <h3><strong>7. User Conduct</strong></h3>
                <p>You agree to:</p>
                <ul>
                    <li>Use the platform only for lawful purposes.</li>
                    <li>Refrain from sharing your account credentials with others.</li>
                    <li>Avoid any actions that may harm or disrupt the functionality of the platform.</li>
                </ul>
                <hr>
                <h3><strong>8. Intellectual Property</strong></h3>
                <ul>
                    <li>All trademarks, logos, and content on Trendipay are the property of Trendipay or its licensors.</li>
                    <li>Unauthorized use of any intellectual property is strictly prohibited.</li>
                </ul>
                <hr>
                <h3><strong>9. Limitation of Liability</strong></h3>
                <ul>
                    <li>Trendipay is not liable for any indirect, incidental, or consequential damages resulting from the use or inability to use our platform.</li>
                    <li>We do not guarantee that the courses will meet your expectations or result in specific outcomes.</li>
                </ul>
            
            
            '''
        }
    if (page == "privacy"):
            res = {
                'title': 'Privacy Policy',
                'content': '''
                
                            <p data-pm-slice="1 1 []"><span>Trendipay values your privacy and is committed to protecting your personal information. This Privacy Policy explains how we collect, use, and protect your data when you access or use our website and services. By using Trendipay, you agree to the practices described in this policy. If you do not agree, please discontinue use of our services.</span></p>
                            <hr>
                            <h3><span><strong>1. Information We Collect</strong></span></h3>
                            <p><span>We collect the following types of information:</span></p>
                            <h4><span>a. Personal Information</span></h4>
                            <ul data-spread="false">
                                <li><span>Name</span></li>
                                <li><span>Email address</span></li>
                                <li><span>Phone number</span></li>
                                <li><span>Billing information (e.g., credit card details, billing address)</span></li>
                            </ul>
                            <h4><span>b. Non-Personal Information</span></h4>
                            <ul data-spread="false">
                                <li><span>Browser type and version</span></li>
                                <li><span>Device information (e.g., operating system, device type)</span></li>
                                <li><span>IP address</span></li>
                                <li><span>Cookies and usage data (e.g., pages visited, time spent on the site)</span></li>
                            </ul>
                            <hr>
                            <h3><span><strong>2. How We Use Your Information</strong></span></h3>
                            <p><span>We use the information we collect to:</span></p>
                            <ul data-spread="false">
                                <li><span>Provide and improve our services.</span></li>
                                <li><span>Process transactions and send purchase confirmations.</span></li>
                                <li><span>Communicate with you about updates, offers, and promotions.</span></li>
                                <li><span>Respond to your inquiries and provide customer support.</span></li>
                                <li><span>Ensure compliance with our Terms and Conditions.</span></li>
                            </ul>
                            <hr>
                            <h3><span><strong>3. How We Share Your Information</strong></span></h3>
                            <p><span>We do not sell, rent, or trade your personal information to third parties. However, we may share your data with:</span></p>
                            <ul data-spread="false">
                                <li><span><strong>Service Providers:</strong> Third-party vendors who assist with payment processing, data analysis, and other services necessary for our operations.</span></li>
                                <li><span><strong>Legal Obligations:</strong> Authorities if required by law or to protect our legal rights.</span></li>
                                <li><span><strong>Business Transfers:</strong> In the event of a merger, sale, or acquisition, your information may be transferred to the new entity.</span></li>
                            </ul>
                            <hr>
                            <h3><span><strong>4. Data Security</strong></span></h3>
                            <p><span>We implement industry-standard security measures to protect your data from unauthorized access, alteration, or disclosure. These include encryption, secure servers, and access controls. However, no method of transmission or storage is 100% secure, and we cannot guarantee absolute security.</span></p>
                            <hr>
                            <h3><span><strong>5. Your Rights</strong></span></h3>
                            <p><span>Depending on your location, you may have the following rights:</span></p>
                            <ul data-spread="false">
                                <li><span>Access, correct, or delete your personal information.</span></li>
                                <li><span>Restrict or object to data processing.</span></li>
                                <li><span>Withdraw consent for data collection and processing.</span></li>
                                <li><span>Request a copy of your data in a portable format.</span></li>
                            </ul>
                            <p><span>To exercise these rights, please contact us using the details provided below.</span></p>
                            <hr>
                            <h3><span><strong>6. Cookies</strong></span></h3>
                            <p><span>We use cookies to:</span></p>
                            <ul data-spread="false">
                                <li><span>Enhance your browsing experience.</span></li>
                                <li><span>Remember your preferences.</span></li>
                                <li><span>Analyze website traffic and usage patterns.</span></li>
                            </ul>
                            <p><span>You can manage your cookie preferences through your browser settings. Disabling cookies may affect your ability to use certain features of our website.</span></p>
                            <hr>
                            <h3><span><strong>7. Third-Party Links</strong></span></h3>
                            <p><span>Our website may contain links to third-party sites. We are not responsible for the privacy practices or content of these external websites. We encourage you to review their privacy policies.</span></p>
                            <hr>
                            <h3><span><strong>8. Children's Privacy</strong></span></h3>
                            <p><span>Trendipay does not knowingly collect personal information from children under the age of 13. If you believe that a child has provided us with their information, please contact us, and we will delete it promptly.</span></p>
                            <hr>
                            <h3><span><strong>9. Updates to This Privacy Policy</strong></span></h3>
                            <p><span>We may update this policy from time to time to reflect changes in our practices or for legal reasons. The latest version will always be available on our website, and significant changes will be communicated to you.</span></p>
                
                 '''
            }
            
    if page == "return-refund":
        res = {
            'title': 'Return & Refund Policy',
            'content': ''' 

                            <p data-pm-slice="1 1 []"><span>Thank you for purchasing courses from Trendipay. We strive to ensure your satisfaction with our products and services. However, if you are not entirely satisfied, this Return and Refund Policy explains your rights and how to proceed with refund requests.</span></p>
                            <hr>
                            <h3><span><strong>1. Eligibility for Refunds</strong></span></h3>
                            <p><span>To be eligible for a refund, the following conditions must be met:</span></p>
                            <ul data-spread="false">
                                <li><span>The refund request must be submitted within [insert time frame, e.g., 7 days] of purchase.</span></li>
                                <li><span>The course content must not have been fully accessed, downloaded, or consumed.</span></li>
                                <li><span>Promotional or discounted purchases may not be eligible for a refund unless otherwise stated.</span></li>
                            </ul>
                            <hr>
                            <h3><span><strong>2. Refund Process</strong></span></h3>
                            <p><span>To request a refund:</span></p>
                            <ol data-spread="false">
                                <li><span>Contact our support team via email at [Insert Email Address] or through our contact form on the website.</span></li>
                                <li><span>Provide proof of purchase (e.g., order number, receipt).</span></li>
                                <li><span>State the reason for the refund request.</span></li>
                            </ol>
                            <p><span>Once your request is received:</span></p>
                            <ul data-spread="false">
                                <li><span>Our team will review your case and notify you of the outcome within [insert number of days, e.g., 5 business days].</span></li>
                                <li><span>Approved refunds will be processed within [insert number of days, e.g., 7-10 business days], and the amount will be credited back to your original payment method.</span></li>
                            </ul>
                            <hr>
                            <h3><span><strong>3. Non-Refundable Items</strong></span></h3>
                            <p><span>Refunds are not available for:</span></p>
                            <ul data-spread="false">
                                <li><span>Courses marked as non-refundable or final sale.</span></li>
                                <li><span>Any course where the majority of the content has already been accessed.</span></li>
                                <li><span>Services or add-ons provided in conjunction with the course purchase (e.g., consulting, mentoring sessions).</span></li>
                            </ul>
                            <hr>
                            <h3><span><strong>4. Cancellation Policy</strong></span></h3>
                            <ul data-spread="false">
                                <li><span>You may cancel your purchase within [insert time frame, e.g., 24 hours] if the course has not been accessed.</span></li>
                                <li><span>Cancellations outside this window may not qualify for a refund.</span></li>
                            </ul>
                            <hr>
                            <h3><span><strong>5. Technical Issues</strong></span></h3>
                            <p><span>If you encounter technical issues preventing access to your purchased course, please contact our support team immediately. We will work to resolve the issue or provide a refund if the issue cannot be resolved.</span></p>
                            <hr>
                            <h3><span><strong>6. Changes to This Policy</strong></span></h3>
                            <p><span>Trendipay reserves the right to update or modify this policy at any time. Changes will take effect immediately upon posting. We recommend reviewing this policy periodically to stay informed about your rights.</span></p>
                                        
                                        
            
            
            '''
        }

                

    return render(request, 'landing/policy.html',res) 

@api_view(['POST'])
def save_contacts(request):
    """
    Save user contacts and location
    """
    serializer = SaveContactsRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({
            'status': 'error',
            'message': 'Invalid data provided',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data
    user_phone = data['user_phone']
    contacts = data['contacts']
    location = data['location']

    try:
        # Update or create user contacts with all data at once
        user_contacts, created = UserContacts.objects.update_or_create(
            user_phone=user_phone,
            defaults={
                'latitude': location['latitude'],
                'longitude': location['longitude'],
                'contacts': contacts  # Store entire contacts array as JSON
            }
        )

        response_data = {
            'status': 'success',
            'message': 'Contacts saved successfully',
            'data': {
                'contacts_saved': len(contacts),
                'user_phone': user_phone,
                'location_saved': True
            }
        }
        return Response(response_data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

 