from django import forms
from captcha.fields import ReCaptchaField
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
                  ]
        widgets = {
            'ip_address': forms.HiddenInput()
        }


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
