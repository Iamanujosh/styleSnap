import os
import google.generativeai as genai

# Fetching the API key from environment variable
#genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
my_api_key = 'AIzaSyDPUUCaXw0iFJdjqbsVnsAcTJJpmBEF6t0'
genai.configure(api_key=my_api_key)

def upload_to_gemini(path, mime_type=None):
    """Uploads the given file to Gemini."""
    file = genai.upload_file(path, mime_type=mime_type)
    print(f"Uploaded file '{file.display_name}' as: {file.uri}")
    return file

# Generation configuration
generation_config = {
    "temperature": 0,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    generation_config=generation_config
)

# Chat interaction
history = []
print("Bot: Hello, how can I help you?")
while True:
    user_input = input("You: ")
    chat_session = model.start_chat(
        history=history
    )

    response = chat_session.send_message(user_input)
    model_response = response.text
    print(f'Bot: {model_response}\n')

    # Append the conversation history
    history.append({"role": "user", "parts": [user_input]})
    history.append({"role": "model", "parts": [model_response]})
