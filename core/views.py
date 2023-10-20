from django.shortcuts import render, redirect, get_object_or_404
from .forms import SubscriptionForm
from .models import Newsletter


def subscribe(request, short_name):
    newsletter: Newsletter = get_object_or_404(Newsletter, short_name=short_name)

    if not newsletter.allows_subscription:
        return render(request, 'subscriptions/newsletter_subscription_closed.html')

    if request.method == 'POST':
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            subscription = form.save(commit=False)
            subscription.ip_address = get_client_ip(request)
            subscription.save()
            # You can add code here to send a confirmation email
            return render(request, 'subscriptions/confirmation.html')
    else:
        context = {
            'short_name': short_name,
            'form': SubscriptionForm(initial={'newsletter': newsletter}),

        }

    return render(request, 'subscriptions/subscribe.html', context)


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
