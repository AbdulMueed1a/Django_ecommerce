
from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    path('register', RegistrationView.as_view()),
    path('verify_email/<str:token>', email_verification),
    path('resend_verify_email', resend_verification_mail),
    path('verify_2fa', resend_verification_mail),

]
