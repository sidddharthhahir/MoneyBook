from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.http import JsonResponse
from django.contrib.auth.models import User
from validate_email import validate_email
import json
from django.contrib import messages
from django.core.mail import EmailMessage
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from .utils import token_generator
import logging
from django.contrib.auth import authenticate, login
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib import auth
from django.contrib.auth import get_user_model
from django.utils.encoding import force_str
import threading

logger = logging.getLogger(__name__)

class EmailThread(threading.Thread):
    def __init__(self, email_message):
        self.email_message = email_message
        threading.Thread.__init__(self)

    def run(self):
        self.email_message.send()

class EmailValidationView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            email = data.get('email', '')

            if not validate_email(email):
                return JsonResponse({'email_error': 'Email is invalid'}, status=400)

            if User.objects.filter(email=email).exists():
                return JsonResponse({'email_error': 'Email is already taken'}, status=409)

            return JsonResponse({'email_valid': True})
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

class UsernameValidationView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            username = data.get('username', '')

            if not username.isalnum():
                return JsonResponse({'username_error': 'Username should only contain letters and numbers'}, status=400)

            if User.objects.filter(username=username).exists():
                return JsonResponse({'username_error': 'Username is already taken'}, status=409)

            return JsonResponse({'username_valid': True})
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

class RegistrationView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'authentication/register.html')
    
    def post(self, request):
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        context = {
            'fieldValues': request.POST
        }

        # Validation
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username is already taken')
            return render(request, 'authentication/register.html', context)
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email is already taken')
            return render(request, 'authentication/register.html', context)
        
        if len(password) < 6:
            messages.error(request, 'Password too short')
            return render(request, 'authentication/register.html', context)

        # Create user
        user = User.objects.create_user(username=username, email=email)
        user.set_password(password)
        user.is_active = False
        user.save()

        # Generate activation link
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        domain = get_current_site(request).domain
        link = reverse('activate', kwargs={'uidb64': uidb64, 'token': token_generator.make_token(user)})
        
        # Send activation email
        email_subject = 'Activate your account'
        activate_url = 'http://' + domain + link
        email_body = f'Hi {user.username}, Please use this link to verify your account:\n{activate_url}'
        
        email_message = EmailMessage(
            email_subject,
            email_body,
            'noreply@semycolon.com',
            [email],
        )
        
        try:
            EmailThread(email_message).start()
            messages.success(request, 'Account successfully created. Please check your email to activate your account.')
        except Exception as e:
            logger.error(f"Email sending failed: {e}")
            messages.error(request, 'Account created but email could not be sent. Please contact support.')
        
        return render(request, 'authentication/register.html')

class VerificationView(View):
    def get(self, request, uidb64, token, *args, **kwargs):
        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = get_object_or_404(User, pk=user_id)

            if not token_generator.check_token(user, token):
                messages.error(request, 'Activation link is invalid')
                return redirect('login')
            
            if user.is_active:
                messages.info(request, 'Account is already activated')
                return redirect('login')
            
            user.is_active = True
            user.save()

            messages.success(request, 'Account activated successfully')
            return redirect('login')
        
        except Exception as ex:
            logger.error(f"Activation error: {ex}")
            messages.error(request, 'Activation failed')
            return redirect('login')

class LoginView(View):
    def get(self, request):
        return render(request, 'authentication/login.html')
    
    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']

        if username and password:
            user = authenticate(username=username, password=password)

            if user:
                if user.is_active:
                    auth.login(request, user)
                    messages.success(request, 'Welcome ' + user.username + ', you are now logged in')
                    return redirect('expenses')  # Add redirect after login
                    # return redirect('expenses') 
                else:
                    messages.error(request, 'Account is disabled')
            else:
                messages.error(request, 'Invalid username or password')
        else:
            messages.error(request, 'Please fill both username and password')
        
        return render(request, 'authentication/login.html')
    
class LogoutView(View):
    def post(self, request):
        auth.logout(request)
        auth.logout(request)
        messages.success(request, 'You have been logged out')
        return redirect('login')
    
class RequestPasswordResetEmail(View):
    def get(self, request):
        return render(request, 'authentication/reset-password.html')

    def post(self, request):
        email = request.POST['email']
        context = {
            'values': request.POST
        }

        if not validate_email(email):
            messages.error(request, 'Please enter a valid email address')
            return render(request, 'authentication/reset-password.html', context)
            
        user = User.objects.filter(email=email)

        if user.exists():
            uidb64 = urlsafe_base64_encode(force_bytes(user[0].pk))
            domain = get_current_site(request).domain
            link = reverse('reset-user-password', kwargs={
                'uidb64': uidb64,
                'token': PasswordResetTokenGenerator().make_token(user[0])
            })
            reset_url = 'http://' + domain + link
            email_subject = 'Password reset'
            email_body = f'Hi {user[0].username}, Please use this link to reset your password:\n{reset_url}'
            
            email_message = EmailMessage(
                email_subject,
                email_body,
                'noreply@semycolon.com',
                [email],
            )
            
            try:
                EmailThread(email_message).start()
                messages.success(request, 'Password reset email has been sent. Please check your inbox.')
            except Exception as e:
                logger.error(f"Email sending failed: {e}")
                messages.error(request, 'Email could not be sent. Please contact support.')
        else:
            messages.error(request, 'No user is associated with this email address.')

        return render(request, 'authentication/reset-password.html')

class CompletePasswordReset(View):
    def get(self, request, uidb64, token):
        context = {
            'uidb64': uidb64,
            'token': token
        }
        
        # Validate the token on GET request too (optional but recommended)
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
            
            if not PasswordResetTokenGenerator().check_token(user, token):
                messages.error(request, 'Password reset link is invalid or expired')
                return render(request, 'authentication/reset-password.html', context)
                
        except (TypeError, ValueError, OverflowError, User.DoesNotExist, UnicodeDecodeError) as ex:
            logger.error(f"Password reset GET error: {ex}")
            messages.error(request, 'Invalid password reset link')
            return render(request, 'authentication/reset-password.html', context)
        
        return render(request, 'authentication/set-new-password.html', context)

    def post(self, request, uidb64, token):
        context = {
            'uidb64': uidb64,
            'token': token
        }

        # First, validate the token and get the user
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)

            if not PasswordResetTokenGenerator().check_token(user, token):
                messages.error(request, 'Password reset link is invalid or expired')
                return render(request, 'authentication/reset-password.html', context)
            
        except (TypeError, ValueError, OverflowError, User.DoesNotExist, UnicodeDecodeError) as ex:
            logger.error(f"Password reset POST error: {ex}")
            messages.error(request, 'Invalid password reset link')
            return render(request, 'authentication/reset-password.html', context)

        # Now validate the passwords
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')

        if password != password2:
            messages.error(request, 'Passwords do not match')
            return render(request, 'authentication/set-new-password.html', context)

        if len(password) < 6:
            messages.error(request, 'Password too short')
            return render(request, 'authentication/set-new-password.html', context)

        # Reset the password
        try:
            user.set_password(password)
            user.save()
            messages.success(request, 'Password reset successfully')
            return redirect('login')
            
        except Exception as ex:
            logger.error(f"Password save error: {ex}")
            messages.error(request, 'Password reset failed')
            return render(request, 'authentication/set-new-password.html', context)