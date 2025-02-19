import uuid
from django.utils import timezone
from django.db import models
from datetime import timedelta

class Loan(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    interest_rate = models.FloatField()
    duration_months = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

class User(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone_number = models.CharField(max_length=15, unique=True, db_index=True)
    name = models.CharField(max_length=100, null=True)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True)
    deleted_at = models.DateTimeField(null=True)

    def __str__(self):
        return self.phone_number

class UserOTP(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone_number = models.CharField(max_length=15, db_index=True)
    otp_code = models.CharField(max_length=100)
    is_used = models.BooleanField(default=False)
    expires_at = models.DateTimeField(default=timezone.now() + timedelta(minutes=5))
    created_at = models.DateTimeField(auto_now_add=True)
    attempt_count = models.IntegerField(default=0)

class UserSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    device_id = models.CharField(max_length=255)
    fcm_token = models.CharField(max_length=255)
    last_active = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    device_info = models.JSONField()

class HomeTopBanner(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    image_url = models.URLField(max_length=200)  # URL for the banner image
    is_live = models.BooleanField(default=True)   # Indicates if the banner is currently live
    title = models.CharField(max_length=100, null=True, blank=True)  # Optional title for the banner
    description = models.TextField(null=True, blank=True)  # Optional description for the banner
    order = models.PositiveIntegerField(default=0)  # Order of the banner for display

    def __str__(self):
        return self.title if self.title else f"HomeTopBanner {self.id}"

class CreditCardCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)  # Category name must be unique
    description = models.TextField(null=True, blank=True)  # Optional description

    def __str__(self):
        return self.name

class CreditCard(models.Model):
    CARD_CATEGORY_CHOICES = [
        ('rewards', 'Rewards'),
        ('travel', 'Travel'),
        ('cashback', 'Cashback'),
        ('business', 'Business'),
        ('student', 'Student'),
        ('secured', 'Secured'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    card_name = models.CharField(
        max_length=255,
        verbose_name='Credit Card Name',
        default='Untitled Card'  # Default card name
    )
    bank_name = models.CharField(
        max_length=255,
        verbose_name='Bank Name',
        default='Unknown Bank'  # Default bank name
    )
    category = models.ForeignKey(
        CreditCardCategory,
        on_delete=models.SET_NULL,
        null=True,
        related_name='credit_cards',
        verbose_name='Card Category'
    )
    annual_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Annual Fee',
        help_text='Annual fee in INR',
        default=0.00  # Default annual fee is 0
    )
    reward_points = models.TextField(
        verbose_name='Reward Points',
        help_text='Description of reward points system',
        default=''  # Empty string as default
    )
    banner_image_url = models.URLField(
        verbose_name='Banner Image URL',
        help_text='URL for the card banner image',
        default=''  # Empty string as default
    )
    referral_url = models.URLField(
        verbose_name='Referral URL',
        help_text='Affiliate/Referral link for the credit card',
        null=True,
        blank=True
    )
    features = models.JSONField(
        default=list,
        verbose_name='Features',
        help_text='List of card features and benefits'
    )
    active_status = models.BooleanField(
        default=True,
        verbose_name='Active Status',
        help_text='Whether the card is currently active'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created At',
        help_text='When this card was added'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Last Updated',
        help_text='When this card was last modified'
    )

    class Meta:
        db_table = 'credit_cards'
        ordering = ['card_name']
        verbose_name = 'Credit Card'
        verbose_name_plural = 'Credit Cards'

    def __str__(self):
        return f"{self.card_name} - {self.bank_name}"

class Policy(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    content = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Policy'
        verbose_name_plural = 'Policies'

    def __str__(self):
        return self.title

class LoanApplication(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    STEP_CHOICES = [
        ('amount', 'Loan Amount'),
        ('personal', 'Personal Information'),
        ('kyc', 'KYC Information'),
        ('professional', 'Professional Information'),
        ('checkout_page', 'Checkout Page'),
    ]

    LOAN_TYPE_CHOICES = [
        ('personal', 'Personal'),
        ('business', 'Business'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    current_step = models.CharField(max_length=20, choices=STEP_CHOICES, default='amount')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Loan Amount Details
    loan_details = models.JSONField(null=True, blank=True)
    # Structure:
    # {
    #     "loanType": "personal" | "business",
    #     "loanAmount": number,
    #     "tenure": number,
    #     "interestRate": number
    # }

    # Personal Information
    personal_info = models.JSONField(null=True, blank=True)
    # Structure:
    # {
    #     "full_name": string,
    #     "email": string,
    #     "residential_state": string,
    #     "residential_address": string?,
    #     "residential_city": string?,
    #     "residential_pincode": string?,
    #     "date_of_birth": string?,
    #     "gender": string?,
    #     "marital_status": string?
    # }

    # KYC Information
    kyc_info = models.JSONField(null=True, blank=True)
    # Structure:
    # {
    #     "panNumber": string,
    #     "aadhaarNumber": string,
    #     "aadhaarPhone": string,
    #     "gstNumber": string?,
    #     "photoIdUrl": string?
    # }

    # Professional/Business Information
    professional_info = models.JSONField(null=True, blank=True)
    # Structure:
    # {
    #     "companyName": string,
    #     "designation": string,
    #     "monthlyIncome": string,
    #     "companyAddress": string,
    #     "workEmail": string?,
    #     "experience": string?,
    #     "isSalaried": boolean?,
    #     "companyType": string?,
    #     "industryType": string?,
    #     "employeeCount": string?,
    #     "annualTurnover": string?,
    #     "businessVintage": string?,
    #     "currentAccountBank": string?,
    #     "upiId": string?
    # }

    class Meta:
        db_table = 'loan_applications'
        ordering = ['-created_at']

    def __str__(self):
        return f"Loan Application {self.id} - {self.status}"

class CheckoutConfig(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    base_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Base Price',
        help_text='Base price for the checkout'
    )
    base_discount_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name='Base Discount Percentage',
        help_text='Base discount percentage to apply',
        default=0.00
    )
    checkout_content = models.JSONField(
        default=list,
        verbose_name='Checkout Content List',
        help_text='List of content items for checkout'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Checkout Configuration'
        verbose_name_plural = 'Checkout Configurations'

    def __str__(self):
        return f"Checkout Config - ₹{self.base_price} ({self.base_discount_percentage}% off)"

class Coupon(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    coupon_code = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='Coupon Code'
    )
    description = models.TextField(
        verbose_name='Description',
        help_text='Description of the coupon'
    )
    discount_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name='Discount Percentage',
        help_text='Discount percentage to apply'
    )
    is_live_to_list = models.BooleanField(
        default=True,
        verbose_name='Is Live',
        help_text='Whether the coupon is live and listable'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Coupon'
        verbose_name_plural = 'Coupons'

    def __str__(self):
        return f"{self.coupon_code} - {self.discount_percentage}% off"

class Payment(models.Model):
    PAYMENT_STATUS = [
        ('initiated', 'Initiated'),
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded')
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    application = models.ForeignKey(LoanApplication, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=100, unique=True)
    gateway = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS)
    gateway_response = models.JSONField(
        null=True, 
        blank=True,
        default=dict,
        help_text='Payment gateway response data'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Payment {self.transaction_id} - {self.status}"

class DeviceToken(models.Model):
    DEVICE_TYPES = [
        ('ios', 'iOS'),
        ('android', 'Android'),
        ('web', 'Web')
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    device_token = models.CharField(max_length=255)
    device_type = models.CharField(max_length=10, choices=DEVICE_TYPES)
    is_active = models.BooleanField(default=True)
    last_active = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'device_token')

class NotificationTemplate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=100)
    body = models.TextField()
    type = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('personal', 'Personal'),
        ('loan', 'Loan'),
        ('payment', 'Payment'),
        ('system', 'System')
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    body = models.TextField()
    type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    is_read = models.BooleanField(default=False)
    metadata = models.JSONField(null=True, blank=True)
    deep_link = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

class NotificationPreference(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    personal_notifications = models.BooleanField(default=True)
    loan_notifications = models.BooleanField(default=True)
    payment_notifications = models.BooleanField(default=True)
    quiet_hours_start = models.TimeField(null=True, blank=True)
    quiet_hours_end = models.TimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True) 