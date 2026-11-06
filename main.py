import json
from voice_engine import speech_to_text, text_to_speech
from Empathy_brain import generate_empathetic_reply, DO_NOT_REPEAT_MEMORY

def run_sahaara_turn(input_audio_path, output_audio_path="sahaara_reply.wav"):
    print("\n1. listening via Gnani Prisma STT...")
    user_text = speech_to_text(input_audio_path)
    print(f"User spoken Text: {user_text}")

    print("\n2. Analyzing Acoustics & Thinking via Gemini 3.5 Flash Brain...")
    brain_data = generate_empathetic_reply(user_text, input_audio_path)
    print(json.dumps(brain_data, indent=2, ensure_ascii=False))
    print(f"DO-NOT-REPEAT MEMORY: {DO_NOT_REPEAT_MEMORY}")

    print("\n3. Speaking via Gnani Timbre TTS...")
    saved_reply= text_to_speech(brain_data["spoken_reply"], output_audio_path)
    print(f" Done! Listen to sahaara's voice reply at: {saved_reply}")
    return brain_data, saved_reply

if __name__ == "__main__":
    run_sahaara_turn("reply.wav")