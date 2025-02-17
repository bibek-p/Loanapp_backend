from django import forms
from .models import CreditCard

class CreditCardForm(forms.ModelForm):
    class Meta:
        model = CreditCard
        fields = [
            'card_name',
            'bank_name',
            'category',
            'annual_fee',
            'reward_points',
            'banner_image_url',
            'referral_url',
            'features',
            'active_status'
        ]
        widgets = {
            'card_name': forms.TextInput(attrs={'class': 'form-control'}),
            'bank_name': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'annual_fee': forms.NumberInput(attrs={'class': 'form-control'}),
            'reward_points': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'banner_image_url': forms.URLInput(attrs={'class': 'form-control'}),
            'referral_url': forms.URLInput(attrs={'class': 'form-control'}),
            'features': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter features as JSON array, e.g.\n[\n  "5X reward points on dining",\n  "Airport lounge access"\n]'
            }),
            'active_status': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_features(self):
        features = self.cleaned_data.get('features')
        if isinstance(features, str):
            try:
                import json
                features = json.loads(features)
                if not isinstance(features, list):
                    raise forms.ValidationError("Features must be a JSON array")
            except json.JSONDecodeError:
                raise forms.ValidationError("Features must be a valid JSON array")
        return features 