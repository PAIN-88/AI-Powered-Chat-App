from django.shortcuts import render,redirect
from .forms import *
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.template.loader import render_to_string

def home(request):
    return render(request, 'user/home.html', {})

def register_view(request):
    email_sent = False
    sent_email_address = None

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.password = make_password(form.cleaned_data['password'])
            user.is_active = False
            user.save()

            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            verify_link = request.build_absolute_uri(f'/verify/{uid}/{token}/')

            send_mail(
                subject='Verify your PAIN account',
                message=f'Hi {user.username},\n\nClick the link below to verify your account:\n{verify_link}',
                from_email=None,
                recipient_list=[user.email],
                fail_silently=False,
            )

            email_sent = True
            sent_email_address = user.email
            form = RegisterForm()  # form reset kar do
    else:
        form = RegisterForm()

    return render(request, 'user/register.html', {
        'form': form,
        'email_sent': email_sent,
        'sent_email_address': sent_email_address,
    })


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            
            try:
                user_obj = User.objects.get(email=email)
                username = user_obj.username
            except  User.DoesNotExist:
                username = None
        
            user = authenticate(request, username=username, password=password)

            if user is not None:
                if not user.is_active:
                    form.add_error(None, "Please verify you email before logging in.")
                else:
                  login(request,user)
                  return redirect('home')
            else:
                form.add_error(None,"Invalid Credentials")
    else:
        form = LoginForm()
    
    return render(request,'user/login.html', {'form':form})


def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def profile_view(request):
    profile = request.user.profile
    return render(request,'user/profile.html',{'profile':profile})


@login_required
def profile_setting(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES ,instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'user/profile_setting.html', {'form':form})

from django.contrib import messages

def verify_email_view(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Your email has been verified! You can now log in.")
        return redirect('login')
    else:
        messages.error(request, "This verification link is invalid or has expired.")
        return redirect('login')