from gpiozero import Button
import azure.cognitiveservices.speech as speechsdk
import openai
import time

AZURE_SPEECH_KEY = "AZURE_SPEECH_KEY"
AZURE_REGION = "AZURE_REGION"
AZURE_OPENAI_KEY = "AZURE_OPENAI_KEY"
AZURE_OPENAI_ENDPOINT = "AZURE_OPENAI_ENDPOINT"

openai.api_key = AZURE_OPENAI_KEY
openai.api_base = AZURE_OPENAI_ENDPOINT
openai.api_type = 'azure'
openai.api_version = '2023-05-15'

BUTTON_PIN = 16
button = Button(BUTTON_PIN)

speech_config = speechsdk.SpeechConfig(subscription=AZURE_SPEECH_KEY, region=AZURE_REGION)

voice_name = "en-US-AndrewMultilingualNeural"
speech_config.speech_synthesis_voice_name = voice_name

speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)
speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)

def ask_openai(prompt):
    response = openai.ChatCompletion.create(
        engine="gpt-35-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=250
    )
    return response['choices'][0]['message']['content'].strip()

def on_button_pressed():
    print("Button pressed! Listening...")

    result = speech_recognizer.recognize_once()

    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        user_input = result.text
        print(f"You said: {user_input}")

        response = ask_openai(user_input)
        print(f"Assistant: {response}")

        speech_synthesizer.speak_text_async(response).get()

    elif result.reason == speechsdk.ResultReason.NoMatch:
        print("No speech could be recognized.")
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        print(f"Speech Recognition canceled: {cancellation_details.reason}")

button.when_pressed = on_button_pressed

print("AI Assistant is ready. Press the button to speak.")
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Program terminated.")
