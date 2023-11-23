from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV3
from django import forms
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe

from .models import SubscriptionToNewsletter
from .models import VisitSurvey


class SubscriptionForm(forms.ModelForm):
    BOOLEAN_CHOICES = [(False, 'No'), (True, 'Yes')]

    subscribe_to_newsletter = forms.ChoiceField(
        label="Would you like to subscribe to the newsletter?",
        choices=BOOLEAN_CHOICES,
        widget=forms.Select,
        initial=False,
        required=False
    )

    captcha = ReCaptchaField(label="reCAPTCHA security verification",)

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
                  'privacy_policy_accepted',
                  ]
        widgets = {
            'ip_address': forms.HiddenInput()
        }
        labels = {
            'privacy_policy_accepted': mark_safe("Please note that accepting the Privacy Policy is mandatory for completing the subscription process.<br>"
                                                 "<strong>Do you accept the Privacy Policy?</strong>"),

            'subscription_to_newsletter': mark_safe("Would you like to subscribe to <strong>BSBF Trieste 2024 newsletter</strong> in order to be updated on the next steps towards BSBF 2024 edition?"),
        }

    def clean(self):
        cleaned_data = super().clean()

        subscribe_to_newsletter = cleaned_data.get("subscribe_to_newsletter")

        # convert subscribe_to_newsletter to boolean
        subscribe_to_newsletter = subscribe_to_newsletter == 'True'


        if subscribe_to_newsletter:
            privacy_policy_accepted = cleaned_data.get("privacy_policy_accepted")
            email = cleaned_data.get("email")
            name = cleaned_data.get("name")
            surname = cleaned_data.get("surname")
            nationality = cleaned_data.get("nationality")
            company = cleaned_data.get("company")
            role = cleaned_data.get("role")
            telephone = cleaned_data.get("telephone")

            if not privacy_policy_accepted:
                print("privacy_policy_accepted is not True")
                raise ValidationError("Accepting the Privacy Policy is mandatory to complete the subscription process to the newsletter.")

            if not email or not name or not surname \
                    or not nationality or not company or not role or not telephone:

                raise ValidationError("Email, name, surname, nationality, company, role, telelephone are mandatory to complete the subscription process to the newsletter.")

        else:
            print("subscribe_to_newsletter is not True")

        return cleaned_data

    def __init__(self, *args, **kwargs):
        super(SubscriptionForm, self).__init__(*args, **kwargs)
        initial_subscribe = self.initial.get('subscribe_to_newsletter', False)
        for field_name in self.fields:
            if field_name != 'subscribe_to_newsletter':
                self.fields[field_name].required = initial_subscribe


class VisitSurveyForm(forms.ModelForm):
    BOOLEAN_CHOICES = [(True, 'Yes'), (False, 'No')]

    participated = forms.ChoiceField(choices=BOOLEAN_CHOICES, widget=forms.Select(), label="Did you participate in the BSBF visit?")
    met_expectations = forms.ChoiceField(choices=BOOLEAN_CHOICES, widget=forms.Select(), label="Did it meet your expectations?")
    interested_in_future_visits = forms.ChoiceField(choices=BOOLEAN_CHOICES, widget=forms.Select(), label="Are you interested in participating in next BSBF visits to CERN, ESA, ESO, ESS, F4E or European XFEL, etc?")
    participate_in_bsbf = forms.ChoiceField(choices=BOOLEAN_CHOICES, widget=forms.Select(), label="Will you participate in the next edition of BSBF in Trieste (IT), 1-4 October 2024?")

    class Meta:
        model = VisitSurvey
        fields = [
            'participated',
            'met_expectations',
            'aspects_made_impression',
            'suggestions_for_improvement',
            'interested_in_future_visits',
            'participate_in_bsbf',
        ]
        widgets = {
            'aspects_made_impression': forms.Textarea(attrs={'rows': 4, 'cols': 40}),
            'suggestions_for_improvement': forms.Textarea(attrs={'rows': 4, 'cols': 40}),
        }