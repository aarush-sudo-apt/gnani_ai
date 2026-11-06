import streamlit as st
from datetime import datetime
from main import run_sahaara_turn
import Empathy_brain
from Empathy_brain import DO_NOT_REPEAT_MEMORY, CONVERSATION_HISTORY

st.set_page_config(
    page_title="Gnani.ai - Voice-first Emotional Companion",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- SESSION STATE INITIALIZATION ----------------
if "ui_messages" not in st.session_state:
    st.session_state.ui_messages = []
if "last_brain" not in st.session_state:
    st.session_state.last_brain = None
if "last_user_text" not in st.session_state:
    st.session_state.last_user_text = "Yaar, main kaafi stressed feel kar raha hoon..."
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "Conversation"
if "autoplay_tts" not in st.session_state:
    st.session_state.autoplay_tts = True

# ---------------- CUSTOM CSS (GLASSMORPHISM + SIDEBAR BUTTONS) ----------------
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, rgba(13, 16, 23, 0.88) 0%, rgba(28, 24, 30, 0.78) 45%, rgba(14, 17, 24, 0.95) 100%),
                    url('https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=1920&q=80');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        color: #f1f5f9;
        font-family: 'Inter', sans-serif;
    }
    header[data-testid="stHeader"] { background: transparent !important; }
    .block-container { padding-top: 1.5rem !important; max-width: 96% !important; }

    /* Sidebar Styling & Interactive Nav Buttons */
    section[data-testid="stSidebar"] {
        background: rgba(14, 16, 22, 0.96) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }
    section[data-testid="stSidebar"] .stButton > button {
        width: 100%;
        text-align: left !important;
        justify-content: flex-start !important;
        padding: 10px 14px !important;
        border-radius: 10px !important;
        font-size: 14px !important;
        margin-bottom: 4px !important;
        background: transparent !important;
        color: #94a3b8 !important;
        border: 1px solid transparent !important;
        box-shadow: none !important;
    }
    section[data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(255, 255, 255, 0.06) !important;
        color: #f8fafc !important;
    }
    section[data-testid="stSidebar"] .stButton > button[kind="primary"] {
        background: linear-gradient(90deg, rgba(212, 163, 115, 0.24), rgba(255, 255, 255, 0.05)) !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        border: 1px solid rgba(212, 163, 115, 0.4) !important;
    }

    .models-box {
        background: rgba(255, 255, 255, 0.04); border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 14px; padding: 15px; margin-top: 45px;
    }
    .model-row {
        display: flex; justify-content: space-between; align-items: center;
        padding: 6px 0; font-size: 13px; color: #e2e8f0;
    }
    .check-badge {
        background: rgba(34, 197, 94, 0.2); color: #4ade80;
        border-radius: 50%; padding: 2px 6px; font-size: 11px;
    }

    /* Glass Panels & Orb */
    .glass-card {
        background: rgba(20, 23, 31, 0.78);
        backdrop-filter: blur(18px);
        border: 1px solid rgba(255, 255, 255, 0.11);
        border-radius: 16px;
        padding: 18px;
        margin-bottom: 14px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.35);
    }
    .challenge-pill {
        float: right; background: rgba(255, 255, 255, 0.07);
        border: 1px solid rgba(255, 255, 255, 0.16); border-radius: 20px;
        padding: 6px 15px; font-size: 13px; color: #f8fafc;
    }
    .orb-wrapper {
        width: 215px; height: 215px; margin: 10px auto 10px auto;
        border-radius: 50%;
        background: radial-gradient(circle at 30% 30%, rgba(226, 176, 121, 0.22), rgba(16, 19, 26, 0.92) 70%);
        border: 1.5px solid rgba(235, 188, 138, 0.45);
        box-shadow: 0 0 50px rgba(226, 176, 121, 0.25), inset 0 0 30px rgba(226, 176, 121, 0.15);
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        text-align: center;
    }
    .orb-bars { color: #e5b37c; font-size: 28px; letter-spacing: 3px; margin-bottom: 6px; }
    .orb-title { font-size: 20px; font-weight: 500; color: #ffffff; }
    .orb-sub { font-size: 12px; color: #94a3b8; margin-top: 3px; }

    .tag-pill {
        display: inline-block; background: rgba(255, 255, 255, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.14); border-radius: 16px;
        padding: 4px 12px; font-size: 12px; color: #e2e8f0; margin-right: 6px; margin-top: 5px;
    }
    .react-inner {
        background: rgba(12, 14, 20, 0.75); border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 10px; padding: 12px; font-size: 12.5px; color: #cbd5e1;
        margin-top: 8px; line-height: 1.55;
    }
    .reject-pill {
        background: rgba(239, 68, 68, 0.13); border: 1px solid rgba(239, 68, 68, 0.3);
        border-radius: 10px; padding: 9px 12px; font-size: 12.5px; color: #fca5a5; margin-bottom: 8px;
    }
    .next-pill {
        background: rgba(34, 197, 94, 0.11); border: 1px solid rgba(34, 197, 94, 0.28);
        border-radius: 10px; padding: 9px 12px; font-size: 12.5px; color: #bbf7d0;
    }
</style>
""", unsafe_allow_html=True)

# ---------------- LEFT SIDEBAR (CLICKABLE NAVIGATION) ----------------
with st.sidebar:
    st.markdown("""<div style="display:flex; align-items:center; gap:10px; margin-bottom:20px;">
<span style="color:#e5b37c; font-size:24px; font-weight:bold;">·|l|·</span>
<div>
<div style="font-size:21px; font-weight:700; color:white; line-height:1.1;">Gnani.ai</div>
<div style="font-size:11px; color:#94a3b8;">Voice-first Emotional Companion</div>
</div>
</div>""", unsafe_allow_html=True)

    nav_options = [
        ("Conversation", "💬  Conversation"),
        ("History", "🕒  History"),
        ("Memory", "🗄️  Do-Not-Repeat Memory"),
        ("Insights", "📊  Insights"),
        ("Settings", "⚙️  Settings")
    ]
    for tab_key, tab_label in nav_options:
        btn_type = "primary" if st.session_state.active_tab == tab_key else "secondary"
        if st.button(tab_label, key=f"nav_{tab_key}", type=btn_type, use_container_width=True):
            st.session_state.active_tab = tab_key
            st.rerun()

    st.markdown(f"""<div class="models-box">
<div style="display:flex; justify-content:space-between; font-size:13px; font-weight:600; margin-bottom:10px; color:#f8fafc;">
<span>🟢   Gnani Models</span><span>ⓘ</span>
</div>
<div class="model-row"><span>🎙️ Prisma STT</span><span class="check-badge">✓</span></div>
<div class="model-row"><span>🧠 ReAct Brain (Key #{Empathy_brain.current_key_index + 1})</span><span class="check-badge">✓</span></div>
<div class="model-row"><span>🔊 Timbre TTS</span><span class="check-badge">✓</span></div>
</div>""", unsafe_allow_html=True)

# ---------------- RIGHT PANEL HELPER (LIVE THINKING + MEMORY) ----------------
def render_right_panel(col):
    with col:
        st.markdown('<div style="height:36px;"><span class="challenge-pill">🏆 Gnani Challenge</span></div>', unsafe_allow_html=True)
        b = st.session_state.last_brain
        stt_preview = st.session_state.last_user_text
        detected_mood = b["detected_emotion"] if b else "Stress / Exhaustion"
        acoustics_txt = b["acoustics"]["acoustic_summary"] if b else "Vocal Energy: High/Tense | Pacing: Steady"
        reasoning_txt = (b["possibility_analysis"] if b else "Thought: User is feeling overwhelmed.<br>Action: Validate feelings first without pressuring.<br>Observation: Warm empathetic reassurance fits best.").replace("\n", "<br>")

        st.markdown(f"""<div class="glass-card">
<div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid rgba(255,255,255,0.08); padding-bottom:10px; margin-bottom:12px;">
<span style="font-size:16px; font-weight:600;">🧠   AI Thinking (ReAct)</span>
<span style="font-size:12px; color:#4ade80;">● Live</span>
</div>
<div style="margin-bottom:14px;">
<div style="font-size:13px; font-weight:600; color:#e2e8f0;">🎙️ Input (Prisma STT)  <span class="check-badge">✓</span></div>
<div style="font-size:12.5px; color:#94a3b8; margin-top:3px;">"{stt_preview}"</div>
</div>
<div style="margin-bottom:14px;">
<div style="font-size:13px; font-weight:600; color:#e2e8f0;">🧡 Emotion & Acoustic Analysis  <span class="check-badge">✓</span></div>
<span class="tag-pill">Emotion: {detected_mood}</span>
<span class="tag-pill">{acoustics_txt}</span>
</div>
<div style="margin-bottom:14px;">
<div style="font-size:13px; font-weight:600; color:#e2e8f0;">🧠 Reasoning (ReAct Possibility Analysis) ⌄</div>
<div class="react-inner">{reasoning_txt}</div>
</div>
<div>
<div style="font-size:13px; font-weight:600; color:#e2e8f0;">🔊 Response (Timbre TTS)  <span class="check-badge">✓</span></div>
<div style="display:flex; justify-content:space-between; font-size:12px; color:#94a3b8; margin-top:4px;">
<span>Voice reply ready</span><span style="color:#e5b37c;">··|l|l|··</span>
</div>
</div>
</div>""", unsafe_allow_html=True)

        mem_items = DO_NOT_REPEAT_MEMORY if DO_NOT_REPEAT_MEMORY else ["Generic time management tips"]
        rejected_html = "".join([f'<div class="reject-pill">✖   <b>Rejected:</b> "{item}"</div>' for item in mem_items])

        st.markdown(f"""<div class="glass-card">
<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
<span style="font-size:15.5px; font-weight:600;">🗄️   Do-Not-Repeat Memory</span>
<span style="font-size:12px; color:#94a3b8;">({len(mem_items)} item)</span>
</div>
{rejected_html}
<div class="next-pill">
✔   <b>Next Time:</b> Provide a more personalized and context-aware empathetic response without repeating rejected advice.
</div>
</div>""", unsafe_allow_html=True)

# ==================== TAB 1: CONVERSATION ====================
if st.session_state.active_tab == "Conversation":
    center_col, right_col = st.columns([1.65, 1.05], gap="large")

    with center_col:
        st.markdown("""<div>
<h1 style="font-size:32px; font-weight:600; margin-bottom:4px; color:white;">Voice-first Emotional Companion</h1>
<p style="font-size:13.5px; color:#cbd5e1; margin-top:0;">A conversational AI that listens, understands your emotions, reasons with empathy, and responds in a natural voice.</p>
</div>
<div class="orb-wrapper">
<div class="orb-bars">··|I|I|··</div>
<div class="orb-title">Listening...</div>
<div class="orb-sub">Speak naturally</div>
</div>""", unsafe_allow_html=True)

        audio_bytes = st.audio_input("🎙️ Tap mic icon to record your voice & speak naturally:")

        if audio_bytes is not None:
            raw_audio = audio_bytes.read()
            if st.session_state.get("last_audio_bytes") != raw_audio:
                st.session_state.last_audio_bytes = raw_audio
                turn_id = len(st.session_state.ui_messages) + 1
                user_wav_path = "user_live.wav"
                ai_wav_path = "sahaara_reply.wav"

                with open(user_wav_path, "wb") as f:
                    f.write(raw_audio)

                with st.spinner("Gnani Prisma STT + ReAct Brain + Timbre TTS processing..."):
                    brain_data, reply_wav = run_sahaara_turn(user_wav_path, ai_wav_path)
                    now_str = datetime.now().strftime("%I:%M %p")
                    latest_user_txt = CONVERSATION_HISTORY[-1]["user"] if CONVERSATION_HISTORY else "Voice Input"

                    with open(reply_wav, "rb") as rf:
                        reply_audio_bytes = rf.read()

                    st.session_state.last_user_text = latest_user_txt
                    st.session_state.last_brain = brain_data
                    st.session_state.ui_messages.append({
                        "turn": turn_id,
                        "time": now_str,
                        "user_text": latest_user_txt,
                        "user_audio_bytes": raw_audio,
                        "ai_text": brain_data["spoken_reply"],
                        "ai_audio_bytes": reply_audio_bytes,
                        "emotion": brain_data["detected_emotion"],
                        "acoustics": brain_data["acoustics"],
                        "reasoning": brain_data["possibility_analysis"]
                    })

        if st.session_state.ui_messages:
            recent_msgs = list(reversed(st.session_state.ui_messages[-2:]))
            for idx, msg in enumerate(recent_msgs):
                st.markdown(f"""<div class="glass-card">
<div style="display:flex; align-items:center; gap:10px; margin-bottom:6px;">
<span style="background:#334155; border-radius:50%; padding:5px 9px;">👤</span>
<span style="font-size:13px; font-weight:600;">You (Turn #{msg['turn']})</span>
<span style="font-size:11.5px; color:#94a3b8;">· {msg['time']}</span>
</div>
<div style="font-size:14px; color:#f1f5f9; margin-top:4px;">"{msg['user_text']}"</div>
</div>""", unsafe_allow_html=True)
                st.audio(msg["user_audio_bytes"], format="audio/wav")

                st.markdown(f"""<div class="glass-card" style="border-color: rgba(229, 179, 124, 0.35);">
<div style="display:flex; align-items:center; gap:10px; margin-bottom:6px;">
<span style="background:rgba(229,179,124,0.2); color:#e5b37c; border-radius:50%; padding:5px 8px;">·|l|·</span>
<span style="font-size:13px; font-weight:600; color:#f8fafc;">Emotional Companion</span>
<span style="font-size:11.5px; color:#94a3b8;">· {msg['time']}</span>
</div>
<div style="font-size:14px; color:#f1f5f9; margin-top:4px;">"{msg['ai_text']}"</div>
</div>""", unsafe_allow_html=True)
                # Autoplay ONLY on the newest message (idx == 0) to prevent DuplicateElementId error!
                should_autoplay = (idx == 0) and st.session_state.autoplay_tts
                st.audio(msg["ai_audio_bytes"], format="audio/wav", autoplay=should_autoplay)
        else:
            st.markdown("""<div class="glass-card">
<div style="display:flex; align-items:center; gap:10px; margin-bottom:8px;">
<span style="background:#334155; border-radius:50%; padding:5px 9px;">👤</span>
<span style="font-size:13px; font-weight:600;">You</span>
<span style="font-size:11.5px; color:#94a3b8;">· Ready</span>
</div>
<div style="font-size:13.5px; color:#cbd5e1;">"Yaar, main kaafi stressed feel kar raha hoon, placements ka pressure hai aur focus bhi maintain nahi ho raha..."</div>
</div>
<div class="glass-card" style="border-color: rgba(229, 179, 124, 0.3);">
<div style="display:flex; align-items:center; gap:10px; margin-bottom:8px;">
<span style="background:rgba(229,179,124,0.2); color:#e5b37c; border-radius:50%; padding:5px 8px;">·|l|·</span>
<span style="font-size:13px; font-weight:600;">Emotional Companion</span>
<span style="font-size:11.5px; color:#94a3b8;">· Ready</span>
</div>
<div style="font-size:13.5px; color:#cbd5e1;">"I can understand, placements ka pressure genuinely stressful hota hai. Upar mic dabao aur khul ke baat karo, main sun raha hoon..."</div>
</div>""", unsafe_allow_html=True)

    render_right_panel(right_col)

# ==================== TAB 2: FULL CONVERSATION HISTORY ====================
elif st.session_state.active_tab == "History":
    st.markdown("<h1 style='color:white;'>🕒 Full Conversation History</h1><p style='color:#cbd5e1;'>Complete log of your spoken interactions, acoustic tags, and empathetic responses.</p>", unsafe_allow_html=True)
    if not st.session_state.ui_messages:
        st.info("Abhi tak koi live voice turn record nahi hua hai. 'Conversation' tab mein jaa kar mic se baat karo!")
    else:
        for msg in reversed(st.session_state.ui_messages):
            st.markdown(f"""<div class="glass-card">
<div style="display:flex; justify-content:space-between; margin-bottom:8px;">
<span style="font-weight:700; color:#e5b37c;">Turn #{msg['turn']} · {msg['time']}</span>
<span class="tag-pill">Mood: {msg['emotion']}</span>
</div>
<p style="color:#f8fafc; margin-bottom:6px;"><b>👤 You:</b> "{msg['user_text']}"</p>
<p style="color:#bbf7d0; margin-bottom:8px;"><b>🌿 Companion:</b> "{msg['ai_text']}"</p>
<div style="font-size:12px; color:#94a3b8;">🎙️ {msg['acoustics']['acoustic_summary']} | 🧠 {msg['reasoning']}</div>
</div>""", unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                st.caption("Your Recorded Voice:")
                st.audio(msg["user_audio_bytes"], format="audio/wav")
            with c2:
                st.caption("Companion Voice Reply:")
                st.audio(msg["ai_audio_bytes"], format="audio/wav")

# ==================== TAB 3: DO-NOT-REPEAT MEMORY ====================
elif st.session_state.active_tab == "Memory":
    st.markdown("<h1 style='color:white;'>🗄️ Do-Not-Repeat Negative Memory Vault</h1><p style='color:#cbd5e1;'>Self-correcting memory block ensuring rejected advice or tones are never repeated.</p>", unsafe_allow_html=True)
    mem_items = DO_NOT_REPEAT_MEMORY if DO_NOT_REPEAT_MEMORY else ["Generic time management tips (Default Demo Rule)"]
    for item in mem_items:
        st.markdown(f'<div class="reject-pill" style="font-size:14px; padding:14px;">✖   <b>Forbidden Approach:</b> "{item}"</div>', unsafe_allow_html=True)

    st.markdown("<div class='glass-card'><h4>➕ Manually Add a Forbidden Advice / Trigger</h4>", unsafe_allow_html=True)
    new_rule = st.text_input("Write any phrase/advice you never want the AI to use (e.g., 'Subah jaldi utho'):")
    col_a, col_b = st.columns([1, 1])
    with col_a:
        if st.button("Add to Do-Not-Repeat Memory") and new_rule.strip():
            DO_NOT_REPEAT_MEMORY.append(new_rule.strip())
            st.success(f"Added '{new_rule}' to forbidden memory!")
            st.rerun()
    with col_b:
        if st.button("🗑️ Clear Custom Memory Rules"):
            DO_NOT_REPEAT_MEMORY.clear()
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# ==================== TAB 4: USER EMOTIONAL & ACOUSTIC INSIGHTS ====================
elif st.session_state.active_tab == "Insights":
    st.markdown("<h1 style='color:white;'>📊 User Emotional & Acoustic Insights</h1><p style='color:#cbd5e1;'>Real-time biometric voice markers and emotional state progression across your session.</p>", unsafe_allow_html=True)
    msgs = st.session_state.ui_messages
    if not msgs:
        st.info("Speak at least once in the 'Conversation' tab to unlock live Librosa acoustic & emotional analytics!")
    else:
        avg_energy = round(sum(m["acoustics"]["vocal_energy"] for m in msgs) / len(msgs), 4)
        avg_pause = round(sum(m["acoustics"]["pause_ratio"] for m in msgs) / len(msgs), 2)
        latest_emotion = msgs[-1]["emotion"]

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Voice Turns", len(msgs))
        m2.metric("Latest Detected Emotion", latest_emotion[:22])
        m3.metric("Avg Vocal Energy (RMS)", avg_energy)
        m4.metric("Avg Silence/Pause Ratio", f"{int(avg_pause * 100)}%")

        st.markdown("<div class='glass-card'><h4>🎙️ Vocal Energy & Pause Ratio Progression</h4></div>", unsafe_allow_html=True)
        chart_data = {
            "Vocal Energy (RMS)": [m["acoustics"]["vocal_energy"] for m in msgs],
            "Pause Ratio": [m["acoustics"]["pause_ratio"] for m in msgs]
        }
        st.line_chart(chart_data)

        st.markdown("<div class='glass-card'><h4>🧠 Turn-by-Turn Emotional Trajectory</h4>", unsafe_allow_html=True)
        for m in msgs:
            st.markdown(f"**Turn #{m['turn']} ({m['time']}):** `{m['emotion']}` — *{m['acoustics']['acoustic_summary']}*")
        st.markdown("</div>", unsafe_allow_html=True)

# ==================== TAB 5: SETTINGS ====================
elif st.session_state.active_tab == "Settings":
    st.markdown("<h1 style='color:white;'>⚙️ System & API Settings</h1><p style='color:#cbd5e1;'>Control your 4-Key Gemini Rotation Pool, Voice Autoplay, and Session Memory.</p>", unsafe_allow_html=True)
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.session_state.autoplay_tts = st.toggle("🔊 Auto-Play Timbre TTS Voice Replies", value=st.session_state.autoplay_tts)

    st.write("---")
    st.subheader("🔑 4-Key Auto-Rotation Pool Manager")
    st.write(f"Currently Active Gemini Key Slot: **Key #{Empathy_brain.current_key_index + 1}** (Total Loaded Keys: `{len(Empathy_brain.GEMINI_KEYS)}`)")
    selected_key = st.selectbox(
        "Manually Switch Active Gemini API Key:",
        options=list(range(len(Empathy_brain.GEMINI_KEYS))),
        format_func=lambda x: f"Gemini API Key #{x + 1}",
        index=Empathy_brain.current_key_index
    )
    if selected_key != Empathy_brain.current_key_index:
        Empathy_brain.current_key_index = selected_key
        st.success(f"Switched active pointer to Gemini API Key #{selected_key + 1}!")

    st.write("---")
    if st.button("🔄 Reset Entire Conversation & Session History"):
        st.session_state.ui_messages.clear()
        st.session_state.last_brain = None
        CONVERSATION_HISTORY.clear()
        st.success("Conversation history cleared!")
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)