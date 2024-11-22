from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import UserLoginForm, UserRegistrationForm
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.http import HttpResponse
from django.core.mail import send_mail
from django.conf import settings
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator



@csrf_protect
def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('index')
            else:
                form.add_error(None, 'Invalid username or password')
    else:
        form = UserLoginForm()
    return render(request, 'authentication/login.html', {'form': form})


def user_logout(request):
    logout(request)
    return redirect('login')


def user_register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'authentication/register.html', {'form': form})


# Password reset using Django's built-in PasswordResetForm
def password_reset(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            form.save()  # Send the password reset email
            messages.success(request, "We have sent you a link to reset your password.")
            return redirect('password_reset_done')  # Redirect to the done page
    else:
        form = PasswordResetForm()

    return render(request, 'authentication/password_reset.html', {'form': form})


def password_reset_done(request):
    """
    View to show the message that a reset link has been sent.
    """
    return render(request, 'authentication/password_reset_done.html')


def password_reset_confirm(request, uidb64, token):
    """
    Custom password reset view. This is used when the user clicks on the reset password link from their email.
    """
    # Decode uidb64 to get the user ID
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = get_user_model().objects.get(id=uid)
    except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        # Valid token and user, now handle the password reset
        if request.method == 'POST':
            new_password1 = request.POST.get('new_password1')
            new_password2 = request.POST.get('new_password2')

            if new_password1 and new_password2:
                if new_password1 == new_password2:  # Ensure the passwords match
                    # Hash the new password and save it
                    user.set_password(new_password1)
                    user.save()

                    # Log the user in automatically after the reset
                    login(request, user)

                    # Redirect to login or success page
                    return redirect('login')
                else:
                    return render(request, 'authentication/password_reset_confirm.html', {'error': 'Passwords do not match'})

        return render(request, 'authentication/password_reset_confirm.html', {'user': user})

    else:
        # If user or token is invalid
        return render(request, 'authentication/password_reset_invalid.html')


def send_mail_page(request):
    context = {}

    if request.method == 'POST':
        address = request.POST.get('address')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        if address and subject and message:
            try:
                send_mail(subject, message, settings.EMAIL_HOST_USER, [address])
                context['result'] = 'Email sent successfully'
            except Exception as e:
                context['result'] = f'Error sending email: {e}'
        else:
            context['result'] = 'All fields are required'
    
    return render(request, "index.html", context)

def password_reset_complete(request):
    """
    View to show the user a success message after password reset completion.
    """
    return render(request, 'authentication/password_reset_complete.html')