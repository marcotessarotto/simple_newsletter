from django.shortcuts import render, redirect
from .forms import SubscriptionForm


def subscribe(request):
    if request.method == 'POST':
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            subscription = form.save(commit=False)
            subscription.ip_address = get_client_ip(request)
            subscription.save()
            # You can add code here to send a confirmation email
            return render(request, 'subscriptions/confirmation.html')
    else:
        form = SubscriptionForm()
    return render(request, 'subscriptions/subscribe.html', {'form': form})


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
