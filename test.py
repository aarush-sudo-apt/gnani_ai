import requests

# Veer's Gnani API Key
API_KEY = "vach_1ytE2CY5X2ERzK0pzUJeJl64djBAE4OerC90JSvfNcDsWqYqQVtR98sndneVRIssXEcEnt1YIhhOfN1z0ZnA6sRquGc5e6qo_e99634421a2dc17edc9fb985ada839d4"
BASE_URL = "https://api.vachana.ai"

def test_tts_and_stt():
    print("1. Testing Gnani Timbre (Text-to-Speech)...")
    tts_url = f"{BASE_URL}/api/v1/tts/inference"
    
    tts_headers = {
        "Content-Type": "application/json",
        "X-API-Key-ID": API_KEY
    }
    
    tts_payload = {
        "text": "नमस्ते आरुष और वीर, आपकी एपीआई की बिल्कुल सही काम कर रही है।",
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

    tts_response = requests.post(tts_url, headers=tts_headers, json=tts_payload)
    
    if tts_response.status_code == 200:
        with open("test_output.wav", "wb") as f:
            f.write(tts_response.content)
        print("SUCCESS! Timbre TTS ne 'test_output.wav' generate kar di hai. Isko play karke suno!\n")
    else:
        print(f"TTS Error ({tts_response.status_code}): {tts_response.text}")
        return

    # Ab isi generated audio file se Prisma STT check karte hain
    print("2. Testing Gnani Prisma (Speech-to-Text)...")
    stt_url = f"{BASE_URL}/stt/v3"
    
    stt_headers = {
        "X-API-Key-ID": API_KEY
    }
    
    with open("test_output.wav", "rb") as audio_file:
        files = {
            "audio_file": ("test_output.wav", audio_file, "audio/wav")
        }
        data = {
            "language_code": "hi-IN"
        }
        stt_response = requests.post(stt_url, headers=stt_headers, files=files, data=data)
        
    if stt_response.status_code == 200:
        print("SUCCESS! Prisma STT Response:")
        print(stt_response.json())
    else:
        print(f"STT Error ({stt_response.status_code}): {stt_response.text}")

if __name__ == "__main__":
    test_tts_and_stt()