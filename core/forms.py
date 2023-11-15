from django import forms
from captcha.fields import ReCaptchaField
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe

from .models import SubscriptionToNewsletter
from .models import VisitSurvey


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
        privacy_policy_accepted = cleaned_data.get("privacy_policy_accepted")

        if not privacy_policy_accepted:
            print("privacy_policy_accepted is not True")
            raise ValidationError("Accepting the Privacy Policy is mandatory to complete the subscription process to the newsletter.")

        return cleaned_data


class VisitSurveyForm(forms.ModelForm):
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
            'participated': forms.RadioSelect(choices=((False, 'No'), (True, 'Yes'))),
            'met_expectations': forms.RadioSelect(choices=((False, 'No'), (True, 'Yes'))),
            'aspects_made_impression': forms.Textarea(attrs={'rows': 4, 'cols': 40}),
            'suggestions_for_improvement': forms.Textarea(attrs={'rows': 4, 'cols': 40}),
            'interested_in_future_visits': forms.RadioSelect(choices=((False, 'No'), (True, 'Yes'))),
            'participate_in_bsbf': forms.RadioSelect(choices=((False, 'No'), (True, 'Yes'))),
        }
        labels = {
            'participated': "Did you participate in the BSBF visit?",
            'met_expectations': "Did it meet your expectations?",
            'aspects_made_impression': "What are the main aspects of the  BSBF visit relevant to you?",
            'suggestions_for_improvement': "What suggestions do you have to improve future BSBF visits to Big Science Organizations?",
            'interested_in_future_visits': "Are you interested in participating in next BSBF visits to CERN, ESA, ESO,  ESS, F4E or European XFEL, etc?",
            'participate_in_bsbf': "Will you participate in the next edition of BSBF in Trieste (IT),  1-4 October 2024?",
        }
