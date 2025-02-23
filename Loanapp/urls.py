from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    UserViewSet, UserOTPViewSet, UserSessionViewSet,
    register_or_login, verify_otp, resend_otp,
    get_live_banners, add_banner, delete_banner,
    add_credit_card_category, get_credit_card_categories,
    update_credit_card_category, delete_credit_card_category,
    add_credit_card, get_credit_cards, update_credit_card, delete_credit_card,
    create_loan_application, update_loan_application,
    get_loan_application, submit_application, get_user_applications,
    credit_card_list_api, credit_card_category_list_api,
    get_checkout_config, get_live_coupons, validate_coupon,
    initiate_phonepe_payment, payment_callback, payment_redirect,
    verify_payment, list_user_loan_applications, get_loan_application_details,
    get_policy_by_title,
    register_device, list_notifications,
    mark_notifications_read, send_notification, notification_settings,
    save_contacts,
)

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'user_otps', UserOTPViewSet)
router.register(r'user_sessions', UserSessionViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('register_or_login/', register_or_login, name='register_or_login'),
    path('verify_otp/', verify_otp, name='verify_otp'),
    path('resend_otp/', resend_otp, name='resend_otp'),
    
    # JWT Token URLs
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # New endpoint for getting live banners
    path('banners/live/', get_live_banners, name='get_live_banners'),

    # New endpoint for adding banners
    path('banners/add/', add_banner, name='add_banner'),

    # New endpoint for deleting a banner by ID
    path('banners/delete/<uuid:banner_id>/', delete_banner, name='delete_banner'),

    # New endpoints for credit card categories
    path('credit-card-categories/add/', add_credit_card_category, name='add_credit_card_category'),
    path('credit-card-categories/', get_credit_card_categories, name='get_credit_card_categories'),
    path('credit-card-categories/update/<uuid:category_id>/', update_credit_card_category, name='update_credit_card_category'),
    path('credit-card-categories/delete/<uuid:category_id>/', delete_credit_card_category, name='delete_credit_card_category'),

    # New endpoints for credit cards
    path('credit-cards/', get_credit_cards, name='get_credit_cards'),
    path('credit-cards/add/', add_credit_card, name='add_credit_card'),
    path('credit-cards/<uuid:card_id>/edit/', update_credit_card, name='update_credit_card'),
    path('credit-cards/<uuid:card_id>/delete/', delete_credit_card, name='delete_credit_card'),

    # New endpoints for loan applications
    path('loan-applications/user', get_user_applications, name='get_user_applications'),
    
    # Application detail routes
    path('loan-applications/<str:application_id>/submit', submit_application, name='submit_application'),
    path('loan-applications/<str:application_id>/details', get_loan_application, name='get_loan_application'),
    path('loan-applications/<str:application_id>/', update_loan_application, name='update_loan_application'),
    
    # Create application route must come last
    path('loan-applications', create_loan_application, name='create_loan_application'),

    # New endpoint for listing credit cards
    path('api/credit-cards/', credit_card_list_api, name='credit_card_list_api'),

    # API endpoint for listing credit card categories
    path('api/credit-card-categories/', credit_card_category_list_api, name='credit_card_category_list_api'),

    # Checkout and Coupon endpoints
    path('checkout/config', get_checkout_config, name='get_checkout_config'),
    path('coupons/live', get_live_coupons, name='get_live_coupons'),
    path('coupons/validate', validate_coupon, name='validate_coupon'),

    # Payment endpoints
    path('payments/create-order', initiate_phonepe_payment, name='initiate_phonepe_payment'),
    path('payments/phonepe/callback', payment_callback, name='payment_callback'),
    path('payments/phonepe/redirect', payment_redirect, name='payment_redirect'),
    path('payments/verify', verify_payment, name='verify_payment'),
    path('loan-applications/list', list_user_loan_applications, name='list_user_loan_applications'),
    path('loan-applications/details', get_loan_application_details, name='get_loan_application_details'),
    path('policies/get-by-title', get_policy_by_title, name='get_policy_by_title'),

    # Notification endpoints
    path('notifications/register-device', register_device, name='register_device'),
    path('notifications/list', list_notifications, name='list_notifications'),
    path('notifications/mark-read', mark_notifications_read, name='mark_notifications_read'),
    path('notifications/send', send_notification, name='send_notification'),
    path('notifications/settings', notification_settings, name='notification_settings'),

    # New endpoint for saving contacts
    path('save-contacts/', save_contacts, name='save_contacts'),
] 