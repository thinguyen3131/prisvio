from django.urls import path
from . import views
from .views import SendValidateEmailVerificationCode, ValidateEmailVerificationCode, EmailPasswordResetRequestView, EmailPasswordResetView

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('signin/', views.signin, name='signin'),
    path('clone/', views.clone_user, name='clone_user'),
    path('webhooks/signup/google', views.google_signup_webhook, name='google_signup_webhook'),
    # path('changepassword/', views.change_password, name='change_password'),
    path('send_email_otp/', SendValidateEmailVerificationCode.as_view(), name='send-email-otp'),
    path('validate_email_otp/', ValidateEmailVerificationCode.as_view(), name='validate-email-otp'),
    path('send_email_reset_password_otp/', EmailPasswordResetRequestView.as_view(), name='send-email-reset-password-otp'),
     path('password_reset/', EmailPasswordResetView.as_view(), name='email-password-reset'),
]