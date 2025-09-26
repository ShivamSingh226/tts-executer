import asyncio
import websockets
import os
from aiohttp import web, WSMsgType
from dotenv import load_dotenv
from google.cloud import texttospeech

# Load environment variables from .env
load_dotenv()

# Set up Google Cloud authentication
GOOGLE_CREDS_PATH = os.getenv(
    "GOOGLE_APPLICATION_CREDENTIALS",
    "/etc/secrets/my-service-account.json"
)

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_CREDS_PATH

# Initialize Google Cloud TTS client
tts_client = texttospeech.TextToSpeechClient()

def synthesize_speech(text):
    if text.strip().startswith("<speak>"):
        input_text = texttospeech.SynthesisInput(ssml=text)
    else:
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


async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    async for msg in ws:
        if msg.type == web.WSMsgType.TEXT:
            audio_bytes = synthesize_speech(msg.data)
            await ws.send_bytes(audio_bytes)

    return ws

async def http_handler(request):
    return web.Response(text="WebSocket TTS server is running.")


async def main():
    app = web.Application()
    app.router.add_get("/", http_handler)       # HTTP root handler
    app.router.add_get("/ws", websocket_handler)  # WebSocket handler

    PORT = int(os.getenv("PORT", 8765))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()

    print(f"Server running on http://0.0.0.0:{PORT} and ws://0.0.0.0:{PORT}/ws")
    await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())

