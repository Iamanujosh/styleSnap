from django.shortcuts import render, redirect
from . import forms
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.models import User
from django.conf import settings
import os
import requests
from django.core.files.storage import FileSystemStorage
# views.py
import os
import google.generativeai as genai
from django.shortcuts import render
from django.http import JsonResponse

# Configure the API key
my_api_key = 'AIzaSyDPUUCaXw0iFJdjqbsVnsAcTJJpmBEF6t0'
genai.configure(api_key=my_api_key)

# Initialize model configuration
# generation_config = {
#     "temperature": 0,
#     "top_p": 0.95,
#     "top_k": 64,
#     "max_output_tokens": 8192,
#     "response_mime_type": "text/plain",
# }

# model = genai.GenerativeModel(
#     model_name="gemini-1.5-pro",
#     generation_config=generation_config
# )

# history = []

# def chatbot(request):
#     if request.method == "POST":
#         user_input = request.POST.get("user_input")
#         chat_session = model.start_chat(history=history)
#         response = chat_session.send_message(user_input)
#         model_response = response.text

#         # Append the conversation history
#         history.append({"role": "user", "parts": [user_input]})
#         history.append({"role": "model", "parts": [model_response]})

#         return render(request, 'chatbot.html', {'bot_response': model_response, 'user_input': user_input})

#     return render(request, 'chatbot.html', {'bot_response': 'Hello, how can I help you?'})

generation_config = {
    "temperature": 0,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(model_name="gemini-1.5-pro", generation_config=generation_config)
history = []

def chatbot(request):
    if request.method == "POST":
        user_input = request.POST.get("user_input")

        if not user_input:
            return JsonResponse({'error': 'No user input provided'}, status=400)

        try:
            chat_session = model.start_chat(history=history)
            response = chat_session.send_message(user_input)
            model_response = response.text

            # Append user and bot messages to the history
            history.append({"role": "user", "parts": [user_input]})
            history.append({"role": "model", "parts": [model_response]})

            # Return JSON response for the bot's reply
            return JsonResponse({'bot_response': model_response, 'history': history})

        except Exception as e:
            # Log the exception
            print(f"Error: {e}")
            return JsonResponse({'error': str(e)}, status=500)

    # Render the initial chat page with existing history
    return render(request, 'chatbot.html', {'messages': history})

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
