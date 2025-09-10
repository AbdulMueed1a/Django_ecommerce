
from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    path('register', RegistrationView.as_view()),
    path('seller_register', seller_registration),
    path('verify_email/<str:token>', email_verification),
    path('resend_verify_email', resend_verification_mail),
    path('verify_2fa', verify_2fa),
    path('password_reset/request', PasswordReset.as_view()),
    path('password_reset/confirm', PasswordReset.as_view()),
]
