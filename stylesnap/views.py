from django.shortcuts import render
from django.http import JsonResponse
from django.core.files.storage import default_storage
import google.generativeai as genai
import os
import base64
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
import os
import requests
from django.core.files.storage import FileSystemStorage
import os
import google.generativeai as genai
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from . import forms
from django.urls import reverse





history = []
# Example: Fetching user data from the database

# Configure Gemini API
# Example mapping

google_api_key = 'AIzaSyAmb11uMRSOS9sAwFSqZbJaOqmFrDpsxTM'
genai.configure(api_key=google_api_key)

# Model configuration
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 0,
    "max_output_tokens": 8192,
}

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]

system_prompt = """
  You are a fashion expert specializing in offering personalized styling advice, fashion trends, outfit suggestions, and wardrobe tips. Your role is to assist the user in exploring fashion choices, boosting their confidence, and helping them express their personal style. You must carefully understand the user's preferences, style goals, and occasions, offering thoughtful responses that inspire creativity and self-expression in fashion.

Your key responsibilities:
1. **Greeting user1**: Greet user user1 first and ask them how they would like help with their fashion choices today. Inquire about their current style preferences, events they are dressing for, or specific wardrobe challenges.
2. **Style Exploration**: Pay close attention to the user’s fashion preferences, color choices, body type, and the occasion they are dressing for. Guide them through creating outfits or enhancing their style.
3. **Supportive Feedback**: Provide encouraging, non-judgmental feedback on their fashion choices. Help them feel confident about their style decisions.
4. **Recommendations**: Based on their input, suggest trendy outfit combinations, styling techniques, or accessories that could elevate their look. Suggest seasonal trends or timeless pieces they can incorporate into their wardrobe.
5. **Styling Tips**: Offer detailed, practical styling tips like how to pair certain colors, accessories, or garments to create a cohesive look. This can include recommendations for casual, formal, or occasion-specific attire.
6. **Response format**: Your responses should be stylish, upbeat, and structured with headings, breaks, and paragraphs for clarity. Use fashionable emojis to enhance the playful tone.
7. **Confidence Boost**: Encourage the user to embrace their unique style, and offer affirmations to boost their confidence in trying new looks or trends.

Important Notes to remember:
   1. Scope of response: Only respond if the input text pertains to fashion or style-related queries.
   2. Sensitivity: Always respond with positivity, and avoid making any assumptions about the user's body image or preferences.
   3. Disclaimer: Accompany your suggestions with the disclaimer: 
   "These fashion tips are intended to inspire creativity. Personal style is all about confidence, so wear what makes you feel great!"
   4. Your insights are invaluable in guiding personal style and fashion confidence. Proceed with enthusiasm and care.
   5. **Response format**: Ensure to include headings, breaks, paragraphs, and stylish emojis for a clear, fun text structure.

Please provide the final response with these 2 headings in bold: **Recommendations** and **Styling Tips**.


   
"""


model = genai.GenerativeModel(
    model_name="gemini-1.5-pro-latest",
    generation_config=generation_config,
    safety_settings=safety_settings,
    system_instruction=system_prompt
)

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
                return redirect('chatbot')  # Redirect to home page after successful login
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
   

def analyze_image(request):
    context = {}

    if request.method == "POST":
        image_file = request.FILES.get('image', None)
        user_input = request.POST.get('user_input', None)

        # Check if an image was uploaded
        if image_file:
            # Save the uploaded image temporarily
            image_path = default_storage.save(f"temp/{image_file.name}", image_file)
            
            with open(image_path, "rb") as image:
                image_data = image.read()

            # Encode image data to Base64
            image_data_base64 = base64.b64encode(image_data).decode('utf-8')

            # Prepare image part
            image_part = {
                "mime_type": image_file.content_type,  # Ensure correct MIME type
                "data": image_data_base64  # Use Base64-encoded string
            }

            prompt_parts = [image_part, system_prompt] if not user_input else [user_input, image_part, system_prompt]

            # Generate response using the model
            response = model.generate_content(prompt_parts)
            
            if response:
                # Format the bot's response into structured HTML
                formatted_response = f"""
                    <h3>🤖 Bot Analysis:</h3>
                    <p>{response.text}</p>
                    <p>For further assistance, please upload more information or ask another question! 😊</p>
                """
                return JsonResponse({'bot_response': formatted_response})

            # Clean up the temporary file
            os.remove(image_path)
        elif user_input:
            context['message'] = "No matching symptoms found. Please provide more details."
    
            
            chat_session = model.start_chat(history=history)
            response = chat_session.send_message(user_input)
            model_response = response.text

            # Append user and bot messages to the history
            history.append({"role": "user", "parts": [user_input]})
            history.append({"role": "model", "parts": [model_response]})

            # Return JSON response for the bot's reply
            context['message'] = history
            print(history)
              # Debug output

            return JsonResponse({
                'bot_response': model_response,
                 # Doctor details if found
                'history': history
            })
        
        else:
            # If neither image nor text is provided, show an error message
            context['error'] = "Please provide an image or text input for analysis."

    return render(request, 'chatbot.html', context)

# def analyze_user_input(user_input):
#     # Convert input to lowercase for easier comparison
#     input_lower = user_input.lower()

#     # List of symptoms
#     symptoms = [
#         "stomach pain",
#         "headache",
#         "fever",
#         "cough",
#         "chest pain",
#         "fatigue",
#         "shortness of breath",
#         "back pain",
#         "nausea",
#         "dizziness",
#         "joint pain",
#         "skin rash",
#         "cold",
#         "insomnia",
#         "anxiety",
#         "urinary problems",
#         "weight loss",
#         "vision changes",
#         "hearing loss",
#         "allergic reactions"
#     ]

#     # Loop through symptoms to find a match
#     for symptom in symptoms:
#         if symptom in input_lower:
#             # Find the recommended doctor based on the symptom
#             recommended_doctor = Doctor.objects.filter(specialization__icontains=symptom).first()
#             return recommended_doctor  # Return the matched doctor

#     return None  # No matching symptom found
