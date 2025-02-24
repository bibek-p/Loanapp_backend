from django.contrib import admin
from django.db import models
from .models import (
    Loan, 
    User, 
    UserOTP, 
    UserSession, 
    HomeTopBanner,
    CreditCardCategory,
    CreditCard,
    Policy,
    LoanApplication,
    CheckoutConfig,
    Coupon,
    UserContacts,
)
from django import forms

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'name', 'is_verified', 'is_active', 'created_at', 'last_login')
    list_filter = ('is_verified', 'is_active')
    search_fields = ('phone_number', 'name')
    ordering = ('-created_at',)

@admin.register(CreditCard)
class CreditCardAdmin(admin.ModelAdmin):
    list_display = ('card_name', 'bank_name', 'category', 'annual_fee', 'active_status', 'created_at')
    list_filter = ('active_status', 'category', 'bank_name')
    search_fields = ('card_name', 'bank_name')
    ordering = ('card_name',)
    list_editable = ('active_status',)
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Basic Information', {
            'fields': ('card_name', 'bank_name', 'category', 'annual_fee')
        }),
        ('Rewards & Features', {
            'fields': ('reward_points', 'features')
        }),
        ('Media', {
            'fields': ('banner_image_url', 'referral_url')
        }),
        ('Status & Timestamps', {
            'fields': ('active_status', 'created_at', 'updated_at')
        }),
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['features'].widget = forms.Textarea(attrs={'rows': 4})
        return form

@admin.register(CreditCardCategory)
class CreditCardCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(HomeTopBanner)
class HomeTopBannerAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_live', 'order')
    list_filter = ('is_live',)
    list_editable = ('is_live', 'order')
    ordering = ('order',)

@admin.register(LoanApplication)
class LoanApplicationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'current_step', 'created_at')
    list_filter = ('status', 'current_step')
    search_fields = ('user__phone_number', 'user__name')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')

    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return self.readonly_fields + ('user',)
        return self.readonly_fields

@admin.register(Policy)
class PolicyAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'created_at', 'updated_at')
    search_fields = ('title', 'content')
    list_filter = ('is_active',)

@admin.register(UserOTP)
class UserOTPAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'otp_code', 'is_used', 'expires_at', 'created_at')
    list_filter = ('is_used',)
    search_fields = ('phone_number',)
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'expires_at')

@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'device_id', 'is_active', 'last_active')
    list_filter = ('is_active',)
    search_fields = ('user__phone_number', 'device_id')
    ordering = ('-last_active',)

@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ('id', 'amount', 'interest_rate', 'duration_months', 'created_at')
    search_fields = ('id',)
    ordering = ('-created_at',)

@admin.register(CheckoutConfig)
class CheckoutConfigAdmin(admin.ModelAdmin):
    list_display = ('id', 'base_price', 'base_discount_percentage', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    search_fields = ('base_price', 'base_discount_percentage')

    fieldsets = (
        ('Price Information', {
            'fields': ('base_price', 'base_discount_percentage')
        }),
        ('Content', {
            'fields': ('checkout_content',),
            'description': 'Enter content items as a JSON array, e.g. ["Item 1", "Item 2"]'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['checkout_content'].widget = forms.Textarea(attrs={
            'rows': 4,
            'placeholder': '[\n  "Access to premium features",\n  "24/7 customer support",\n  "Priority processing"\n]'
        })
        return form

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('coupon_code', 'discount_percentage', 'is_live_to_list', 'created_at')
    list_filter = ('is_live_to_list', 'discount_percentage')
    search_fields = ('coupon_code', 'description')
    list_editable = ('is_live_to_list',)
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Coupon Information', {
            'fields': ('coupon_code', 'description', 'discount_percentage')
        }),
        ('Status', {
            'fields': ('is_live_to_list',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['description'].widget = forms.Textarea(attrs={
            'rows': 3,
            'placeholder': 'Enter a detailed description of the coupon...'
        })
        return form

@admin.register(UserContacts)
class UserContactsAdmin(admin.ModelAdmin):
    list_display = ('user_phone', 'latitude', 'longitude', 'created_at')
    search_fields = ('user_phone',)
    readonly_fields = ('created_at', 'updated_at')

    def get_contacts_count(self, obj):
        return len(obj.contacts)
    get_contacts_count.short_description = 'Number of Contacts'

    list_display = ('user_phone', 'latitude', 'longitude', 'get_contacts_count', 'created_at') 