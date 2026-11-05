import os 
import json
import requests
import librosa
import numpy as np
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GNANI_API_KEY")

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
    acoustics = extract_acoustic_cues(audio_path)
    
    url = "https://api.vachana.ai/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "X-API-Key-ID": API_KEY
    }
    
    user_context = f"""
    User Spoken Text: {user_text}
    Acoustic Cues: {acoustics['acoustic_summary']}
    DO_NOT_REPEAT_MEMORY (Forbidden Approaches): {DO_NOT_REPEAT_MEMORY}
    Recent History: {CONVERSATION_HISTORY[-4:]}
    """

    payload = {
        "model": "Evon-30B" , 
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_context}

        ],
        "temperature": 0.6,
        "response_format": {"type": "json_object"}


    }

    response = requests.post(url, headers=headers, json=payload)
    print("Evon server ne yeh bheja:", response.json())
    raw_content = response.json()["choices"][0]["message"]["content"]
    brain_output = json.loads(raw_content)

    if brain_output.get("user_disagreed") and brain_output.get("new_rejected_item"):
        DO_NOT_REPEAT_MEMORY.append(brain_output["new_rejected_item"])

    CONVERSATION_HISTORY.append({"user": user_text, "ai": brain_output["spoken_reply"]})
    brain_output["acoustics"] = acoustics

    return brain_output

    
if __name__ == "__main__":
    test_text = "यार आज बहुत थकान हो गई है, कुछ समझ नहीं आ रहा।"
    result = generate_empathetic_reply(test_text, "reply.wav")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    