import asyncio
import os
import sys

# Add project root to path
sys.path.append(os.getcwd())

from phoenix.audio.local import LocalSTT, LocalTTS

async def test_audio_flow():
    print("\n" + "="*50)
    print("PHOENIX AI: AUDIO SERVICE TEST")
    print("="*50)

    # 1. Test STT
    print("\n[1/2] Testing Local STT (Transcription)...")
    stt = LocalSTT()
    await stt.init()
    
    dummy_audio = "tests/test_audio.wav"
    # Create a dummy file
    with open(dummy_audio, "wb") as f:
        f.write(b"RIFF....WAVEfmt ")
    
    print(f"[*] Transcribing {dummy_audio}...")
    try:
        text = await stt.transcribe(dummy_audio)
        print(f"[v] Success! Transcription: {text}")
    except Exception as e:
        print(f"[!] STT Error: {e}")

    # 2. Test TTS
    print("\n[2/2] Testing Local TTS (Synthesis)...")
    tts = LocalTTS()
    await tts.init()
    
    output_audio = "tests/output_speech.mp3"
    input_text = "Welcome to Phoenix AI SDK."
    print(f"[*] Synthesizing text: '{input_text}'")
    
    try:
        result_path = await tts.synthesize(input_text, output_audio)
        if os.path.exists(result_path):
            print(f"[v] Success! Generated audio at: {result_path}")
        else:
            print("[!] Error: Output file not created.")
    except Exception as e:
        print(f"[!] TTS Error: {e}")

    # Cleanup
    for f in [dummy_audio, output_audio]:
        if os.path.exists(f):
            os.remove(f)

    print("\n" + "="*50)
    print("AUDIO SERVICE TEST COMPLETE")
    print("="*50 + "\n")

if __name__ == "__main__":
    asyncio.run(test_audio_flow())
