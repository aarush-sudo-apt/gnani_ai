import os 
import json
import requests
import librosa
import numpy as np
from dotenv import load_dotenv

load_dotenv()

# Upar GEMINI_KEYS wali line ko aise likh (taaki agar koi key None ho toh 404 na aaye):
GEMINI_KEYS = [k.strip() for k in [
    os.getenv("GEMINI_KEY_1"),
    os.getenv("GEMINI_KEY_2"),
    os.getenv("GEMINI_KEY_3"),
    os.getenv("GEMINI_KEY_4")
] if k]
current_key_index = 0

def extract_acoustic_cues(audio_path):
    y, sr = librosa.load(audio_path , sr=16000)

    rms = librosa.feature.rms(y=y)
    avg_energy = float(np.mean(rms))

    non_silent = librosa.effects.split(y, top_db=25)

    speech_samples = sum(end - start for start, end in non_silent)
    pause_ratio = 1.0 - (speech_samples / len(y)) if len(y) > 0 else 0.0

    energy_tag = "low/Exhausted" if avg_energy < 0.02 else ("High/Tense" if avg_energy>0.08 else "Moderate/calm")
    pause_tag = "Frequent/Hesitant Pauses" if pause_ratio > 0.40 else "Steady Flow"

    return {
        "vocal_energy": round(avg_energy, 4),
        "pause_ratio": round(pause_ratio, 2),
        "acoustic_summary": f"Vocal Energy: {energy_tag} | Pacing: {pause_tag}"

    }


DO_NOT_REPEAT_MEMORY = []
CONVERSATION_HISTORY = []

SYSTEM_PROMPT = """
You are Sahaara, a deeply empathetic Hinglish mental wellness friend.

Follow this exact ReAct process before replying:
1. MULTIMODAL FUSION: Combine User Text + Acoustic Cues to detect true hidden emotion and check if the user disagreed with your last reply.
2. NEGATIVE MEMORY CHECK: If the user disagreed or resisted, extract the rejected advice/tone so we never repeat it. Never use anything listed in DO_NOT_REPEAT_MEMORY.
3. POSSIBILITY ANALYSIS: Briefly evaluate 2 possible response angles and pick the one that best matches the user's current emotional bandwidth.
4. 4-STAGE HINGLISH REPLY: Write your spoken reply in natural Hinglish (2-3 warm sentences max) following:
   - Validation (normalize their feeling, e.g., 'aisa lagna bilkul laazmi hai, par isko apna final conclusion mat banao')
   - Cognitive Reframing + Low-Pressure Trial (only if they are ready, suggest a tiny step)
   - Unconditional Reassurance ('outcome jaisa bhi ho, main tere saath hoon, befikar reh')

Respond STRICTLY in this JSON format:
{
  "detected_emotion": "true mood combining text + acoustics",
  "user_disagreed": true or false,
  "new_rejected_item": "rejected advice if user_disagreed is true, else null",
  "possibility_analysis": "Angle A vs Angle B and why chosen angle fits best",
  "spoken_reply": "Final 4-stage Hinglish response to be converted to audio"
}
"""

def generate_empathetic_reply(user_text, audio_path):
    global current_key_index
    acoustics = extract_acoustic_cues(audio_path)
    
    user_context = f"""
    User Spoken Text: {user_text}
    Acoustic Cues: {acoustics['acoustic_summary']}
    DO_NOT_REPEAT_MEMORY (Forbidden Approaches): {DO_NOT_REPEAT_MEMORY}
    Recent History: {CONVERSATION_HISTORY[-4:]}
    """
    
    payload = {
        "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "contents": [{"parts": [{"text": user_context}]}],
        "generationConfig": {
            "temperature": 0.6,
            "responseMimeType": "application/json"
        }
    }

    # Sabse stable aur low-traffic models ki priority list:
    MODELS_TO_TRY = [
       "gemini-3.5-flash",
        "gemini-3.7-flash",
        "gemini-3.6-flash",
        "gemini-3.5-flash-lite",
        "gemini-3.8-flash"
    ]

    for model_name in MODELS_TO_TRY:
        for attempt in range(len(GEMINI_KEYS)):
            active_key = GEMINI_KEYS[current_key_index]
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={active_key}"
            
            response = requests.post(url, json=payload)
            
            if response.status_code == 200:
                print(f"✅ Success with Model: {model_name} (Key {current_key_index + 1})")
                raw_content = response.json()["candidates"][0]["content"]["parts"][0]["text"]
                brain_output = json.loads(raw_content)
                
                if brain_output.get("user_disagreed") and brain_output.get("new_rejected_item"):
                    DO_NOT_REPEAT_MEMORY.append(brain_output["new_rejected_item"])
                    
                CONVERSATION_HISTORY.append({"user": user_text, "ai": brain_output["spoken_reply"]})
                brain_output["acoustics"] = acoustics
                return brain_output
            
            elif response.status_code == 503:
                print(f"⚠️ {model_name} server busy (503). Trying next model immediately...")
                break  # Server busy hai toh key badalne se fayda nahi, seedha agla model pakdo!
            else:
                print(f"⚠️ Key {current_key_index + 1} limit/error ({response.status_code}). Shifting key...")
                current_key_index = (current_key_index + 1) % len(GEMINI_KEYS)
                
    raise Exception("Saare models aur keys fail ho gayin!")
if __name__ == "__main__":
    test_text = "यार आज बहुत थकान हो गई है, कुछ समझ नहीं आ रहा।"
    result = generate_empathetic_reply(test_text, "reply.wav")
    print(json.dumps(result, indent=2, ensure_ascii=False))
