from .views import RegistrationView, UsernameValidationView, EmailValidationView, RequestPasswordResetEmail, CompletePasswordReset, LoginView, VerificationView, LogoutView
from django.urls import path
from django.views.decorators.csrf import csrf_exempt, csrf_protect



urlpatterns = [
    path('register/', RegistrationView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('activate/<uidb64>/<token>', VerificationView.as_view(), name='activate'),
    path('validate-username', csrf_exempt(UsernameValidationView.as_view()), name="validate_username"),
    path('validate-email', csrf_exempt(EmailValidationView.as_view()), name="validate_email"),
    path('activate/<uidb64>/<token>', csrf_protect(RegistrationView.as_view()), name="activate"),
    path('set-new-password/<uidb64>/<token>', csrf_protect(CompletePasswordReset.as_view()), name="reset-user-password"),
    path('request-password', RequestPasswordResetEmail.as_view(), name="request-password"),

]

