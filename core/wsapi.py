from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Newsletter
from .serializers import SubscriptionToNewsletterSerializer


class SubscriptionCreateView(APIView):
    def post(self, request, *args, **kwargs):
        newsletter_id = request.data.get('newsletter_id')  # Get visit_id from the data

        # Validate visit_id
        if not Newsletter.objects.filter(id=newsletter_id).exists():
            return Response({"error": "Newsletter not found."}, status=status.HTTP_404_NOT_FOUND)

        # Remove visit_id from request.data as it's no longer needed in the serializer directly
        data = request.data.copy()
        # data.pop('visit_id', None)

        serializer = SubscriptionToNewsletterSerializer(data=data)
        if serializer.is_valid():
            # Create the subscription instance
            subscription = serializer.save()
            subscription.newsletter = Newsletter.objects.get(id=newsletter_id)  # Assign the visit manually
            subscription.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
