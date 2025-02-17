from rest_framework import serializers
from .models import Loan, User, UserOTP, UserSession, HomeTopBanner, CreditCardCategory, CreditCard, Policy, LoanApplication, CheckoutConfig, Coupon

class LoanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = ['id', 'amount', 'interest_rate', 'duration_months', 'created_at']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'phone_number', 'name', 'is_verified', 'is_active', 'created_at', 'last_login', 'deleted_at']

class UserOTPSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserOTP
        fields = ['id', 'phone_number', 'otp_code', 'is_used', 'expires_at', 'created_at', 'attempt_count']

class UserSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSession
        fields = ['id', 'user', 'device_id', 'fcm_token', 'last_active', 'is_active', 'device_info']

class OTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)
    otp_code = serializers.CharField(max_length=6)

class HomeTopBannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomeTopBanner
        fields = ['id', 'image_url', 'is_live', 'title', 'description', 'order']

    def validate(self, attrs):
        # Check if the banner is live
        if attrs.get('is_live', False):
            # Check if there is already a live banner with the same image_url
            if HomeTopBanner.objects.filter(image_url=attrs['image_url'], is_live=True).exists():
                raise serializers.ValidationError("A live banner with this image URL already exists.")
        return attrs

class CreditCardCategorySerializer(serializers.ModelSerializer):
    card_count = serializers.SerializerMethodField()

    class Meta:
        model = CreditCardCategory
        fields = [
            'id',
            'name',
            'description',
            'card_count'
        ]

    def get_card_count(self, obj):
        return obj.credit_cards.filter(active_status=True).count()

    def validate(self, attrs):
        # Ensure the category name is unique
        if CreditCardCategory.objects.filter(name=attrs['name']).exists():
            raise serializers.ValidationError("A category with this name already exists.")
        return attrs

class CreditCardSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = CreditCard
        fields = [
            'id',
            'card_name',
            'bank_name',
            'category',
            'category_name',
            'annual_fee',
            'reward_points',
            'banner_image_url',
            'referral_url',
            'features',
            'active_status',
            'created_at',
            'updated_at',
        ]

class PolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = Policy
        fields = ['id', 'title', 'content', 'created_at', 'updated_at']

class LoanApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanApplication
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')
        extra_kwargs = {
            'loan_details': {'required': False},
            'personal_info': {'required': False},
            'kyc_info': {'required': False},
            'professional_info': {'required': False},
        }

    def validate_loan_details(self, value):
        if value and isinstance(value, dict):
            required_fields = {
                'loan_type': str,
                'loan_amount': (int, float)
            }
            
            for field, field_type in required_fields.items():
                if field not in value:
                    raise serializers.ValidationError(f"Missing required field: {field}")
                if not isinstance(value[field], field_type):
                    raise serializers.ValidationError(f"Invalid type for field: {field}")
            
            # Additional validations
            if value['loan_type'] not in ['personal', 'business']:
                raise serializers.ValidationError("Invalid loan type")
            
            if not (10000 <= float(value['loan_amount']) <= 1000000):
                raise serializers.ValidationError("Loan amount must be between ₹10,000 and ₹10,00,000")
        else:
            return {}  # Return empty dict for null/invalid values
        
        return value

    def validate_personal_info(self, value):
        if value is not None:
            required_fields = ['full_name', 'email', 'residential_state']
            if not all(field in value for field in required_fields):
                raise serializers.ValidationError("Missing required fields in personal information")
        return value

    def validate_kyc_info(self, value):
        if value is not None:
            required_fields = ['panNumber', 'aadhaarNumber']
            if not all(field in value for field in required_fields):
                raise serializers.ValidationError("Missing required fields in KYC information")
        return value

    def validate_professional_info(self, value):
        if value is not None:
            required_fields = ['company_name', 'designation', 'monthly_income', 'office_address']
            if not all(field in value for field in required_fields):
                raise serializers.ValidationError("Missing required fields in professional information")
        return value

class CheckoutConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = CheckoutConfig
        fields = [
            'id',
            'base_price',
            'base_discount_percentage',
            'checkout_content',
            'created_at',
            'updated_at'
        ]

class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = [
            'id',
            'coupon_code',
            'description',
            'discount_percentage',
            'is_live_to_list',
            'created_at',
            'updated_at'
        ] 