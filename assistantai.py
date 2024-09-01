from gpiozero import Button
import azure.cognitiveservices.speech as speechsdk
import openai
import time

# Configure your Azure API keys and settings
AZURE_SPEECH_KEY = "765176c6484941919452f50ccac6a48e"
AZURE_REGION = "eastus"
AZURE_OPENAI_KEY = "b7ddc878d4144584a4c7fb2fe8975539"
AZURE_OPENAI_ENDPOINT = "https://gpaiassistant.openai.azure.com/"

# Set up OpenAI using Azure OpenAI Service
openai.api_key = AZURE_OPENAI_KEY
openai.api_base = AZURE_OPENAI_ENDPOINT
openai.api_type = 'azure'
openai.api_version = '2023-05-15'  # Use the version appropriate for your setup

# Configure the button on GPIO 16
BUTTON_PIN = 16
button = Button(BUTTON_PIN)

# Set up Azure Speech Service
speech_config = speechsdk.SpeechConfig(subscription=AZURE_SPEECH_KEY, region=AZURE_REGION)

# Set the voice name for Azure Speech Synthesis (optional, you can choose any available voice)
voice_name = "en-US-AndrewMultilingualNeural"
speech_config.speech_synthesis_voice_name = voice_name

# Initialize the Speech Recognizer and Speech Synthesizer
speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)
speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)

def ask_openai(prompt):
    response = openai.ChatCompletion.create(
        engine="gpt-35-turbo",  # Adjust the model name if necessary
        messages=[{"role": "user", "content": prompt}],
        max_tokens=250
    )
    return response['choices'][0]['message']['content'].strip()

def on_button_pressed():
    print("Button pressed! Listening...")

    # Start speech recognition
    result = speech_recognizer.recognize_once()

    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        user_input = result.text
        print(f"You said: {user_input}")

        # Send the recognized speech to OpenAI
        response = ask_openai(user_input)
        print(f"Assistant: {response}")

        # Use Azure to synthesize the response
        speech_synthesizer.speak_text_async(response).get()

    elif result.reason == speechsdk.ResultReason.NoMatch:
        print("No speech could be recognized.")
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        print(f"Speech Recognition canceled: {cancellation_details.reason}")

# Set the function to run when the button is pressed
button.when_pressed = on_button_pressed

print("AI Assistant is ready. Press the button to speak.")
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Program terminated.")
