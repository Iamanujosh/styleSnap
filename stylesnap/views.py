from django.shortcuts import render, redirect
from . import forms
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.models import User

def home_view(request):
    return render(request,'home.html')

def login_view(request):
    if request.method == 'POST':
        form = forms.LoginForm(request, data=request.POST)
        
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                return redirect('chat')  # Redirect to home page after successful login
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid form submission.')

    else:
        form = forms.LoginForm()

    return render(request, 'login.html', {'form': form})

def register_view(request):
    if request.method == 'POST':
        form = forms.RegisterForm(request.POST)
        if form.is_valid():
            form.save()  # This saves the user to the database
            return redirect('login')  # Redirect to login page after registration
    else:
        form = forms.RegisterForm()
    
    return render(request, 'register.html', {'form': form})

def chat_view(request):
    return render(request, 'chat.html')

