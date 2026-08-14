from django.shortcuts import render,redirect
from .forms import *
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.decorators import login_required

def home(request):
    return render(request, 'user/home.html', {})

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.password = make_password(form.cleaned_data['password'])
            user.save()
            return redirect('login')
    
    else:
        form = RegisterForm()
    
    return render(request,'user/register.html', {'form':form})



def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                form.add_error(None, "Invalid Credentials")
    else:
        form = LoginForm()

    return render(request, 'user/login.html', {'form': form})

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