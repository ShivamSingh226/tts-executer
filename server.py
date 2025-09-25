import asyncio
import websockets
import os
from dotenv import load_dotenv
from google.cloud import texttospeech

# Load environment variables from .env
load_dotenv()

# Set up Google Cloud authentication
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

# Initialize Google Cloud TTS client
tts_client = texttospeech.TextToSpeechClient()

def synthesize_speech(text):
    input_text = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        name="en-US-Wavenet-D"  # You can change this to other supported voices
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.LINEAR16,
        sample_rate_hertz=8000 # PCM format
    )

    response = tts_client.synthesize_speech(
        input=input_text,
        voice=voice,
        audio_config=audio_config
    )

    return response.audio_content

async def handle_client(websocket):
    async for message in websocket:
        print(f"Received text: {message}")

        # Convert text to speech
        audio_bytes = synthesize_speech(message)

        # Send audio bytes back to client
        await websocket.send(audio_bytes)

async def main():
    async with websockets.serve(handle_client, "localhost", 8765, max_size=None,
    ping_interval=30,
    ping_timeout=30
):
        print("Server running on ws://localhost:8765")
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())
