from django import forms
from captcha.fields import ReCaptchaField
from .models import SubscriptionToNewsletter


class SubscriptionForm(forms.ModelForm):
    captcha = ReCaptchaField()

    class Meta:
        model = SubscriptionToNewsletter
        fields = ['honorific',
                  'email',
                  'name',
                  'surname',
                  'nationality',
                  'company',
                  'role',
                  'telephone',
                  ]
        widgets = {
            'ip_address': forms.HiddenInput()
        }
