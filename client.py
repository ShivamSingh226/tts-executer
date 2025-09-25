import asyncio
import websockets
import io
import sounddevice as sd
import soundfile as sf

async def send_and_play():
    uri = "ws://localhost:8765/ws"
    async with websockets.connect(uri) as websocket:
        while True:
            # 1️⃣ User inputs text
            text = input("You: ")
            await websocket.send(text)

            # 2️⃣ Receive audio bytes from server
            audio_bytes = await websocket.recv()
            audio_file = io.BytesIO(audio_bytes)

            # 3️⃣ Decode WAV and play
            data, samplerate = sf.read(audio_file, dtype='float32')
            sd.play(data, samplerate)
            sd.wait()  # Wait until audio finishes

asyncio.run(send_and_play())
