from rest_framework import serializers
from .models import SubscriptionToNewsletter, Newsletter


class SubscriptionToNewsletterSerializer(serializers.ModelSerializer):
    newsletter_id = serializers.PrimaryKeyRelatedField(
        source='newsletter',  # Map newsletter_id to the newsletter ForeignKey
        queryset=Newsletter.objects.all(),
        write_only=True  # Only used for incoming data, not serialized in responses
    )

    class Meta:
        model = SubscriptionToNewsletter
        fields = [
            'newsletter_id', 'honorific', 'email', 'name', 'surname', 'nationality',
            'company', 'role', 'telephone', 'ip_address', 'subscription_source',
            'privacy_policy_accepted', 'subscribed', 'subscription_confirmed'
        ]

    def validate_email(self, value):
        # Validation to ensure email does not exist for an active subscription with the same newsletter
        if self.initial_data.get('newsletter_id') and SubscriptionToNewsletter.objects.filter(
                email=value, subscribed=True, newsletter_id=self.initial_data.get('newsletter_id')).exists():
            raise serializers.ValidationError("A subscription with this email already exists for this newsletter.")
        return value

    def validate_privacy_policy_accepted(self, value):
        if not value:
            raise serializers.ValidationError("You must accept the privacy policy.")
        return value
