from rest_framework import serializers
from .models import SubscriptionToNewsletter


class SubscriptionToNewsletterSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionToNewsletter
        fields = '__all__'  # Or specify the fields you want to expose
        fields = ['honorific',
                  'email',
                  'name',
                  'surname',
                  'nationality',
                  'company',
                  'role',
                  'telephone',
                  'ip_address',
                  'subscription_source',
                  'privacy_policy_accepted',
                  'subscribed',
                  'subscription_confirmed',
                  'newsletter_id']

    def validate_email(self, value):
        """
        Check that the email does not already exist for an active subscription.
        """

        newsletter_id = self.initial_data.get('newsletter_id', None)

        if SubscriptionToNewsletter.objects.filter(email=value, subscribed=True, newsletter_id=newsletter_id).exists():
            raise serializers.ValidationError("A subscription with this email already exists.")
        return value

    def validate_privacy_policy_accepted(self, value):
        """
        Check that the privacy policy has been accepted.
        """

        if not value:
            raise serializers.ValidationError("You must accept the privacy policy.")
        return value
