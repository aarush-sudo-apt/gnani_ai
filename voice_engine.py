import os 
import requests 
from dotenv import load_dotenv
import librosa
import soundfile as sf
import time

load_dotenv()
API_KEY = os.getenv("GNANI_API_KEY")
print("our API key is loaded or not?->", API_KEY)

def speech_to_text(audio_file_path):
    url = "https://api.vachana.ai/stt/v3"
    headers = {
        "X-API-Key-ID": API_KEY
    }
    
    # Fix 1: Browser mic audio ko clean 16kHz Mono WAV mein normalize karo (taaki Gnani STT kabhi timeout na ho)
    clean_path = "clean_stt_input.wav"
    try:
        y, sr = librosa.load(audio_file_path, sr=16000, mono=True)
        sf.write(clean_path, y, 16000, subtype="PCM_16")
    except Exception:
        clean_path = audio_file_path

    # Fix 2: 2-Attempt Auto-Retry & Safe JSON Check
    for attempt in range(2):
        with open(clean_path, "rb") as f:
            files = {
                "audio_file": ("audio.wav", f, "audio/wav")
            }
            data = {
                "language_code": "hi-IN"
            }
            response = requests.post(url, headers=headers, files=files, data=data)
            
        if response.status_code == 200 and response.text.strip():
            try:
                result = response.json()
                return result.get("transcript") or result.get("text") or "Kuch sunai nahi diya..."
            except Exception:
                pass
                
        print(f"⚠️ Gnani STT retry {attempt + 1} (Status {response.status_code}): {response.text[:100]}")
        time.sleep(1)
        
    return "Aawaz thodi saaf nahi aayi yaar, ek baar phir se bolna?"


def text_to_speech(reply_text, output_path="reply.wav"):
    url= "https://api.vachana.ai/api/v1/tts/inference"
    headers= {
        "Content-Type": "application/json",
        "X-API-Key-ID": API_KEY
    }

    payload = {
        "text": reply_text,
        "voice": "Nalini",
        "model": "timbre-v2.5",
        "language": "hi-IN",
        "speed": 1.0,
        "audio_config": {
            "sample_rate": 16000,
            "num_channels": 1,
            "sample_width": 2,
            "encoding": "linear_pcm",
            "container": "wav"
        }
    }

    response = requests.post(url, headers=headers, json=payload)

    with open(output_path, "wb") as audio_file:
        audio_file.write(response.content)

    return output_path 


# Step 1: Pehle Text se Audio banate hain (isse 'reply.wav' khud ban jayegi!)
#saved_audio = text_to_speech("Yaar aaj bohot thakaan ho gayi hai, kuch samajh nahi aa raha.")
#print("Audio file ban gayi:", saved_audio)

# Step 2: Ab usi bani hui 'reply.wav' ko wapas Speech-to-Text mein bhej kar check karte hain!
#result = speech_to_text(saved_audio)
#print("Server ne audio sunke yeh text wapas bheja:", result)
