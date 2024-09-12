from django.shortcuts import render, redirect
from . import forms
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.models import User
from django.conf import settings
import os
import requests
from django.core.files.storage import FileSystemStorage

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
    if request.method == 'POST':
        if 'photo' in request.FILES:
            # Process the uploaded photo
            photo = request.FILES['photo']
            fs = FileSystemStorage()
            filename = fs.save(photo.name, photo)
            uploaded_file_url = fs.url(filename)
            
            # Send the photo to the Gemini API for styling suggestions
            api_key = settings.GEMINI_API_KEY
            api_url = "https://gemini-api-url.com/analyze"  # Replace with the actual Gemini API URL
            
            # Send the image to the API
            with open(fs.path(filename), 'rb') as img_file:
                files = {'file': img_file}
                headers = {'Authorization': f'Bearer {api_key}'}
                response = requests.post(api_url, files=files, headers=headers)
                
                if response.status_code == 200:
                    # Process API response
                    suggestions = response.json().get('suggestions')
                else:
                    suggestions = "Sorry, we couldn't process your request at the moment."
            
            return render(request, 'chat.html', {
                'uploaded_file_url': uploaded_file_url,
                'suggestions': suggestions,
            })
        
        elif 'message' in request.POST:
            # Handle text-based chat
            user_message = request.POST.get('message')
            
            # Here you can integrate Gemini API or process user messages
            # Example logic: send user message to the Gemini API for responses
            api_key = settings.GEMINI_API_KEY
            api_url = "https://gemini-api-url.com/chat"
            data = {'message': user_message}
            headers = {'Authorization': f'Bearer {api_key}'}
            
            response = requests.post(api_url, json=data, headers=headers)
            if response.status_code == 200:
                suggestions = response.json().get('response')
            else:
                suggestions = "Sorry, we couldn't process your request at the moment."
            
            return render(request, 'chat.html', {
                'user_message': user_message,
                'suggestions': suggestions,
            })
    return render(request, 'chat.html')    
