import os 
import requests 
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GNANI_API_KEY")
print("our API key is loaded or not?->", API_KEY)

def speech_to_text(audio_path):
    url = "https://api.vachana.ai/stt/v3"
    headers = {"X-API-Key-ID": API_KEY}
    data = {"language_code": "hi-IN"}

    with open(audio_path, "rb") as audio_file:
        files = {"audio_file": ("input.wav", audio_file, "audio/wav")}
        response = requests.post(url, headers=headers, data=data, files=files)

    #print("STT Status Code:", response.status_code, "| Raw Text:", response.text)
    result = response.json()
    return result["transcript"]
 


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
saved_audio = text_to_speech("Yaar aaj bohot thakaan ho gayi hai, kuch samajh nahi aa raha.")
print("Audio file ban gayi:", saved_audio)

# Step 2: Ab usi bani hui 'reply.wav' ko wapas Speech-to-Text mein bhej kar check karte hain!
result = speech_to_text(saved_audio)
print("Server ne audio sunke yeh text wapas bheja:", result)
