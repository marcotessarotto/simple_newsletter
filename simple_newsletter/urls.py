"""
URL configuration for simple_newsletter project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from core import views
from core.views import proxy_django_auth
from simple_newsletter import settings

urlpatterns = [
    path('admin/', admin.site.urls),

    path('survey_newsletter_subscription/<str:short_name>/', views.survey_newsletter_subscription,
         name='survey_newsletter_subscription'),

    # path('visit_survey_newsletter_subscription/<uuid:token>/', views.visit_survey_newsletter_subscription,
    #      name='visit_survey_newsletter_subscription'),

    path('subscribe/<str:short_name>/', views.subscribe, name='subscribe'),

    path('unsubscribe/<uuid:token>/', views.unsubscribe, name='unsubscribe'),

    path('confirm-subscription/<uuid:token>/', views.confirm_subscription,
            name='confirm_subscription'),

    path('ckeditor/', include('ckeditor_uploader.urls')),

    # used by nginx to verify authentication and access to media files.
    path('proxy_django_auth/', proxy_django_auth, name='proxy_django_auth'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
