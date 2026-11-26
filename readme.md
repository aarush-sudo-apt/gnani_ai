# 🎙️ Sahaara AI (सहारा)

**Multimodal Acoustic-Aware Empathetic Voice Companion with Self-Correcting Negative Memory**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Gnani.ai](https://img.shields.io/badge/Voice-Gnani.ai%20Prisma%20%26%20Timbre-e5b37c)](https://www.gnani.ai/)
[![Gemini](https://img.shields.io/badge/Brain-Gemini%20Flash%20ReAct-4285F4?logo=google&logoColor=white)](https://ai.google.dev/)

Built for the **Gnani.ai Voice Challenge 2026** by **Aarush Aery** & **Veer Vikram Singh Rana** (*Amity University Punjab*).

---

## Overview

Most conversational wellness assistants rely solely on text transcripts, missing critical paralinguistic cues like vocal exhaustion, tension, and hesitation pauses. Worse, standard bots lack negative feedback memory—when a stressed user pushes back on unhelpful advice, the assistant repeats the same generic suggestions, increasing frustration.

**Sahaara AI** is a voice-first, culturally grounded Hinglish companion that treats voice as a multimodal signal. It fuses real-time acoustic features with a structured ReAct reasoning engine and maintains a live **Do-Not-Repeat Negative Memory Vault** that detects user pushback and permanently prunes rejected advice or tones during the session.

---

## Key Features

- **Voice-First Hinglish Pipeline:** Real-time speech capture normalized to 16kHz PCM_16 mono, transcribed via **Gnani Prisma STT** (`hi-IN`) and synthesized into natural conversational Hinglish audio via **Gnani Timbre TTS** (`timbre-v2.5`, `Nalini` voice).
- **Acoustic Biometric Extraction:** Uses `librosa` to measure vocal RMS energy (exhausted vs. calm vs. tense) and silence/pause ratios (steady flow vs. hesitant pacing) directly from raw user audio.
- **Structured ReAct Empathy Brain:** Combines transcript text, acoustic markers, recent conversation history, and forbidden approaches to perform Pre-Response Possibility Analysis before generating a 2–3 sentence warm Hinglish reply.
- **Self-Correcting Negative Memory Loop:** Detects user disagreement or resistance (via both LLM classification and apology/pushback safeguards) and logs rejected advice into `DO_NOT_REPEAT_MEMORY` so the assistant never doubles down on unwanted guidance.
- **Zero-Crash Multi-Model & Multi-Key Cascade:** Rotates across up to 4 Gemini API keys and cascades across 5 Gemini Flash models automatically on rate limits or `503` server overload responses.
- **Interactive Telemetry Dashboard:** A 5-tab Streamlit glassmorphic interface featuring live voice recording, real-time ReAct thought inspection, acoustic progression charts, manual memory controls, and API key pool management.

---

## System Architecture

```text
┌──────────────────────┐
│  User Voice Input    │  (Streamlit Mic / .wav file)
└──────────┬───────────┘
           │
     ┌─────┴─────────────────────────────┐
     ▼                                   ▼
┌─────────────────────────┐   ┌───────────────────────────────┐
│  Gnani Prisma STT       │   │  Librosa Acoustic Engine      │
│  • 16kHz Mono PCM_16    │   │  • RMS Vocal Energy           │
│  • hi-IN Code-Mixing    │   │  • Silence / Pause Ratio      │
│  • 2-Attempt Auto-Retry │   │  • Paralinguistic Tagging     │
└──────────┬──────────────┘   └───────────────┬───────────────┘
           │                                  │
           └──────────────┬───────────────────┘
                          ▼
         ┌────────────────────────────────┐
         │  Gemini Flash ReAct Brain      │◄───┐
         │  1. Multimodal Emotion Fusion  │    │
         │  2. Pushback Detection         │    │  DO_NOT_REPEAT_MEMORY
         │  3. Possibility Analysis       │────┘  (Self-Correcting Vault)
         │  4. Natural Hinglish Reply     │
         └────────────────┬───────────────┘
                          ▼
         ┌────────────────────────────────┐
         │  Gnani Timbre TTS              │
         │  • Model: timbre-v2.5 (Nalini) │
         │  • Output: 16kHz Linear PCM    │
         └────────────────┬───────────────┘
                          ▼
         ┌────────────────────────────────┐
         │  Streamlit Live Dashboard      │
         │  Audio Playback + Telemetry UI │
         └────────────────────────────────┘
```

---

## Acoustic & ReAct Logic

### Acoustic Thresholds (`Empathy_brain.py`)
| Metric | Computation | Tag Mapping |
| :--- | :--- | :--- |
| **Vocal Energy (RMS)** | Mean frame-level `librosa.feature.rms` | `< 0.02` → `low/Exhausted`<br>`> 0.08` → `High/Tense`<br>Otherwise → `Moderate/calm` |
| **Pause Ratio** | `1 - (non_silent_samples / total_samples)` using `top_db=25` | `> 0.40` → `Frequent/Hesitant Pauses`<br>Otherwise → `Steady Flow` |

### Strict JSON Reasoning Output
Each turn enforces structured JSON output (`responseMimeType: "application/json"`) containing:
- `detected_emotion` — Combined mood derived from spoken text and acoustic markers.
- `user_disagreed` — Boolean flag triggered on user pushback or resistance.
- `new_rejected_item` — Short 4–8 word rule appended to `DO_NOT_REPEAT_MEMORY`.
- `possibility_analysis` — Comparison of two candidate response angles and why the chosen direction fits best.
- `spoken_reply` — Final conversational Hinglish reply passed to Timbre TTS.

### Failover Cascade
The reasoning engine cascades through models in priority order:
`gemini-3.5-flash` → `gemini-3.7-flash` → `gemini-3.6-flash` → `gemini-3.5-flash-lite` → `gemini-3.8-flash`.
- **`503` (Server Busy):** Immediately advances to the next model in the cascade.
- **Rate Limits / Other API Errors:** Rotates to the next available key in `GEMINI_KEY_1`–`GEMINI_KEY_4`.

---

## Project Structure

```text
Sahaara_AI/
├── app.py              # 5-tab Streamlit glassmorphic dashboard & audio UI
├── main.py             # Core turn orchestrator (STT → ReAct Brain → TTS) & CLI runner
├── Empathy_brain.py    # Librosa acoustic extraction, Gemini ReAct engine & negative memory
├── voice_engine.py     # Gnani Prisma STT (with audio normalization) & Timbre TTS client
├── README.md           # Project documentation
└── .gitignore          # Excludes .env, *.wav, __pycache__/, and test.py
```

---

## Dashboard Tabs (`app.py`)

1. **💬 Conversation:** Record live voice turns, inspect the live AI Thinking (ReAct) card on the right panel, monitor active Do-Not-Repeat rules, and listen to auto-played Timbre TTS responses.
2. **🕒 History:** Full reverse-chronological log of every turn with transcripts, acoustic summaries, ReAct reasoning, and playback for both user and companion audio.
3. **🗄️ Do-Not-Repeat Memory:** Inspect automatically captured pushback rules, manually add forbidden phrases/triggers, or clear custom rules.
4. **📊 Insights:** Live session KPIs (turn count, latest mood, average RMS vocal energy, average pause ratio), dual-metric line chart, and turn-by-turn emotional trajectory.
5. **⚙️ Settings:** Toggle TTS autoplay, inspect or manually switch the active Gemini API key slot, and reset conversation history.

---

## Getting Started

### Prerequisites
- Python 3.10 or higher
- A **Gnani.ai (Vachana)** API key with access to Prisma STT and Timbre TTS
- 1 to 4 **Google Gemini API** keys

### 1. Clone the Repository
```bash
git clone [https://github.com/](https://github.com/)<your-username>/Sahaara_AI.git
cd Sahaara_AI
```

### 2. Create a Virtual Environment & Install Dependencies
```bash
python -m venv venv

# Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# macOS / Linux
source venv/bin/activate

pip install streamlit requests python-dotenv librosa soundfile numpy
```

### 3. Configure Environment Variables
Create a `.env` file in the root directory:
```env
GNANI_API_KEY=your_gnani_api_key_here
GEMINI_KEY_1=your_primary_gemini_key
GEMINI_KEY_2=your_backup_gemini_key_2
GEMINI_KEY_3=your_backup_gemini_key_3
GEMINI_KEY_4=your_backup_gemini_key_4
```
*(Only `GEMINI_KEY_1` is strictly required; keys 2–4 are automatically loaded if present for rotation.)*

### 4. Run the Application

**Launch the Streamlit Web Dashboard:**
```bash
streamlit run app.py
```

**Or run a single pipeline turn via CLI** *(requires a `reply.wav` file in the project root)*:
```bash
python main.py
```

---

## Tech Stack

- **Frontend & Audio UI:** Streamlit (`st.audio_input`, custom glassmorphic CSS)
- **Speech-to-Text:** Gnani.ai Prisma STT (`v3`, `hi-IN`)
- **Text-to-Speech:** Gnani.ai Timbre TTS (`timbre-v2.5`, `Nalini`)
- **Acoustic Signal Processing:** Librosa, SoundFile, NumPy
- **LLM Reasoning Engine:** Google Gemini Flash REST API (multi-model & multi-key rotation)
- **Configuration:** `python-dotenv`, `requests`

---

## Authors

- **Veer Vikram Singh Rana** — Amity University Punjab
- **Aarush Aery** — Amity University Punjab