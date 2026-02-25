import streamlit as st
from groq import Groq
from elevenlabs import ElevenLabs
from dotenv import load_dotenv
from duckduckgo_search import DDGS
from deep_translator import GoogleTranslator
import fitz
import os
import io
import csv
import tempfile
import requests
import base64
import speech_recognition as sr
import pandas as pd
import re
import json
from auth import (
    init_db, register_user, login_user, save_message, load_history,
    clear_history, get_user_info, get_all_users, change_user_role,
    create_session, get_sessions, rename_session, delete_session,
    export_history_text, save_reaction, check_rate_limit,
    record_message_usage, save_token_usage, get_token_usage,
    request_password_reset, verify_reset_token, reset_password
)

load_dotenv()
init_db()

def get_secret(key):
    try:
        return st.secrets[key]
    except:
        return os.getenv(key, "")

groq_client = Groq(api_key=get_secret("GROQ_API_KEY"))
eleven_client = ElevenLabs(api_key=get_secret("ELEVENLABS_API_KEY"))

# ── FIX 1: NAME CHANGED ──
st.set_page_config(page_title="SmartBot AI", page_icon="🤖", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&display=swap');

* { font-family: 'Inter', sans-serif !important; box-sizing: border-box; }

#MainMenu { visibility: hidden !important; }
header[data-testid="stHeader"] { display: none !important; }
footer { visibility: hidden !important; }
.stDeployButton { display: none !important; }
[data-testid="stToolbar"] { display: none !important; }

.stApp > div:first-child { padding-top: 0 !important; }
.block-container { padding-top: 1rem !important; }

[data-testid="stSidebar"] { min-width: 260px !important; width: 260px !important; display: block !important; visibility: visible !important; transform: translateX(0) !important; }
[data-testid="collapsedControl"] { display: none !important; }
section[data-testid="stSidebar"] > div { width: 260px !important; }

[data-testid="stChatMessage"] [data-testid="stChatMessageAvatarUser"] { display: none !important; }
[data-testid="stChatMessage"] [data-testid="stChatMessageAvatarAssistant"] { display: none !important; }
.stChatMessage > div:first-child { display: none !important; }

/* ── FIX 2: CHAT INPUT VISIBLE ON CLOUD ── */
[data-testid="stBottom"] {
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e) !important;
    border-top: 1px solid rgba(255,255,255,0.08) !important;
}
[data-testid="stBottom"] > div { background: transparent !important; }
[data-testid="stChatInput"] {
    background: rgba(30,25,80,0.95) !important;
    border: 1.5px solid rgba(124,58,237,0.5) !important;
    border-radius: 14px !important;
}
[data-testid="stChatInput"] textarea {
    color: #ffffff !important;
    background: transparent !important;
    font-size: 15px !important;
    caret-color: #a78bfa !important;
}
[data-testid="stChatInput"] textarea::placeholder {
    color: rgba(200,180,255,0.55) !important;
}

.stButton > button { white-space: nowrap !important; overflow: hidden !important; text-overflow: ellipsis !important; font-size: 13px !important; padding: 8px 12px !important; }

[data-testid="stSidebar"] div[data-key="nav_chat"] button,
[data-testid="stSidebar"] div[data-key="nav_profile"] button {
    opacity: 0 !important; height: 0 !important; padding: 0 !important;
    margin: 0 !important; overflow: hidden !important; pointer-events: none !important; border: none !important;
}

.stApp { background: linear-gradient(135deg, #0f0c29, #302b63, #24243e) !important; }
.stApp *, .stApp p, .stApp span, .stApp div, .stApp label,
.stApp h1, .stApp h2, .stApp h3, .stApp h4,
[data-testid="stSidebar"] * { color: white !important; }

input[type="text"], input[type="password"], input[type="email"],
.stTextInput input, .stChatInput textarea {
    background: rgba(30, 25, 80, 0.85) !important; color: #ffffff !important;
    border: 1.5px solid rgba(124,58,237,0.4) !important; border-radius: 12px !important;
    padding: 12px 16px !important; font-size: 15px !important;
}
input[type="text"]:focus, input[type="password"]:focus,
.stTextInput input:focus, .stChatInput textarea:focus {
    border: 1.5px solid #7c3aed !important; outline: none !important;
    background: rgba(40, 32, 100, 0.95) !important;
}
input::placeholder, .stTextInput input::placeholder, .stChatInput textarea::placeholder {
    color: rgba(200, 180, 255, 0.55) !important; font-size: 14px !important;
}
.stTextInput > div > div { background: rgba(30, 25, 80, 0.85) !important; border-radius: 12px !important; }
[data-baseweb="input"], [data-baseweb="base-input"] { background: rgba(30, 25, 80, 0.85) !important; color: white !important; }
[data-baseweb="input"] input, [data-baseweb="base-input"] input { color: white !important; background: transparent !important; }
[data-baseweb="input"] input::placeholder { color: rgba(200, 180, 255, 0.55) !important; }
.stSelectbox > div > div { background: rgba(255,255,255,0.08) !important; color: white !important;
    border: 1.5px solid rgba(255,255,255,0.2) !important; border-radius: 12px !important; }
.stButton > button {
    background: linear-gradient(90deg, #7c3aed, #4f46e5) !important; color: white !important;
    border: none !important; border-radius: 12px !important; padding: 12px 24px !important;
    font-size: 15px !important; font-weight: 600 !important; width: 100% !important;
    cursor: pointer !important; transition: all 0.3s !important;
}
.stButton > button:hover { transform: translateY(-2px) !important; box-shadow: 0 8px 25px rgba(124,58,237,0.5) !important; }
.stTabs [data-baseweb="tab-list"] { background: rgba(255,255,255,0.05) !important; border-radius: 12px !important; padding: 4px !important; gap: 4px !important; }
.stTabs [data-baseweb="tab"] { background: transparent !important; color: rgba(255,255,255,0.6) !important; border-radius: 10px !important; font-weight: 500 !important; padding: 10px 24px !important; }
.stTabs [aria-selected="true"] { background: linear-gradient(90deg, #7c3aed, #4f46e5) !important; color: white !important; }
[data-testid="stChatMessage"] { background: rgba(255,255,255,0.06) !important; border-radius: 16px !important;
    padding: 16px !important; margin: 8px 0 !important; border: 1px solid rgba(255,255,255,0.08) !important; }
[data-testid="stChatMessage"] p { color: white !important; font-size: 15px !important; line-height: 1.6 !important; }
section[data-testid="stSidebar"] { background: rgba(15,12,41,0.95) !important; border-right: 1px solid rgba(255,255,255,0.08) !important; }
[data-testid="stFileUploader"] { background: rgba(255,255,255,0.05) !important; border: 2px dashed rgba(124,58,237,0.5) !important; border-radius: 12px !important; padding: 10px !important; }
[data-testid="stFileUploader"] * { color: white !important; }
.feature-badge { background: rgba(124,58,237,0.25); border: 1px solid rgba(124,58,237,0.5); border-radius: 20px;
    padding: 5px 14px; font-size: 12px; color: #c4b5fd !important; display: inline-block; margin: 3px; font-weight: 500; }
.stat-card { background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.1); border-radius: 14px; padding: 16px; text-align: center; }
.divider { height: 1px; background: rgba(255,255,255,0.1); margin: 16px 0; }

.code-wrapper { position: relative; margin: 10px 0; }
.code-block {
    background: #0d1117 !important; border: 1px solid rgba(255,255,255,0.1);
    border-radius: 0 0 12px 12px; padding: 16px;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 13px; line-height: 1.6; overflow-x: auto; white-space: pre;
    color: #e6edf3 !important; margin: 0;
}
.code-header {
    background: rgba(255,255,255,0.07); border-radius: 12px 12px 0 0;
    padding: 7px 14px; display: flex; justify-content: space-between; align-items: center;
    font-size: 12px; color: rgba(255,255,255,0.5) !important;
    border: 1px solid rgba(255,255,255,0.1); border-bottom: none;
}
.copy-btn {
    background: rgba(124,58,237,0.25); border: 1px solid rgba(124,58,237,0.4);
    border-radius: 6px; padding: 3px 10px; font-size: 11px; color: #c4b5fd !important;
    cursor: pointer; transition: all 0.2s; font-family: inherit;
}
.copy-btn:hover { background: rgba(124,58,237,0.5); color: white !important; }
.kw  { color: #ff79c6 !important; } .str { color: #f1fa8c !important; }
.cmt { color: #6272a4 !important; font-style: italic; } .fn2 { color: #50fa7b !important; }
.num { color: #bd93f9 !important; } .cls { color: #8be9fd !important; }

.plus-btn button {
    background: linear-gradient(135deg,#7c3aed,#4f46e5) !important; border-radius: 50% !important;
    width: 42px !important; height: 42px !important; padding: 0 !important;
    font-size: 20px !important; min-width: 0 !important; box-shadow: 0 4px 14px rgba(124,58,237,0.45) !important;
}
.popup-btn button {
    background: rgba(124,58,237,0.15) !important; border: 1px solid rgba(124,58,237,0.35) !important;
    border-radius: 10px !important; padding: 8px 14px !important; font-size: 13px !important;
    font-weight: 500 !important; width: auto !important; min-width: 0 !important; transition: all 0.2s !important;
}
.popup-btn button:hover { background: rgba(124,58,237,0.4) !important; border-color: rgba(124,58,237,0.8) !important; }
.remove-badge-btn button {
    background: rgba(239,68,68,0.2) !important; border: 1px solid rgba(239,68,68,0.4) !important;
    border-radius: 50% !important; width: 28px !important; height: 28px !important;
    padding: 0 !important; font-size: 13px !important; min-width: 0 !important; color: #fca5a5 !important;
}
.remove-badge-btn button:hover { background: rgba(239,68,68,0.5) !important; }
.file-badge {
    display: inline-flex; align-items: center; gap: 8px;
    background: rgba(124,58,237,0.18); border: 1px solid rgba(124,58,237,0.45);
    border-radius: 24px; padding: 6px 14px 6px 10px; font-size: 13px;
    color: #c4b5fd !important; font-weight: 500; animation: badgeIn 0.2s ease;
}
@keyframes badgeIn { from{opacity:0;transform:scale(0.92)} to{opacity:1;transform:scale(1)} }
.file-badge .fn { color: #e2d9ff !important; font-weight: 600; max-width: 200px;
    overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.file-badge .st { color: rgba(167,139,250,0.7) !important; font-size: 11px; }

.ctx-banner { border-radius: 12px; padding: 10px 16px; font-size: 13px;
    display: flex; align-items: center; gap: 8px; margin-bottom: 6px; }
.ctx-pdf  { background: rgba(34,197,94,0.12);  border: 1px solid rgba(34,197,94,0.35);  color: #6ee7b7 !important; }
.ctx-file { background: rgba(59,130,246,0.12);  border: 1px solid rgba(59,130,246,0.35);  color: #93c5fd !important; }
.ctx-img  { background: rgba(245,158,11,0.12);  border: 1px solid rgba(245,158,11,0.35);  color: #fcd34d !important; }

.profile-card { background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 20px; padding: 28px; margin-bottom: 16px; }
.profile-avatar { width: 72px; height: 72px; background: linear-gradient(135deg,#7c3aed,#4f46e5);
    border-radius: 50%; display: flex; align-items: center; justify-content: center;
    font-size: 32px; margin: 0 auto 16px auto; }
.stat-grid { display: grid; grid-template-columns: repeat(3,1fr); gap: 12px; margin-top: 16px; }
.stat-item { background: rgba(124,58,237,0.15); border: 1px solid rgba(124,58,237,0.3); border-radius: 12px; padding: 14px; text-align: center; }
.stat-num { font-size: 22px; font-weight: 700; color: #a78bfa !important; }
.stat-lbl { font-size: 11px; color: rgba(255,255,255,0.5) !important; margin-top: 2px; }

[data-testid="stSidebar"] div[data-key="nav_chat"] button,
[data-testid="stSidebar"] div[data-key="nav_profile"] button {
    padding: 2px 8px !important; font-size: 11px !important;
    background: transparent !important; border: none !important;
    box-shadow: none !important; width: auto !important;
    opacity: 0.01 !important; height: 4px !important;
    overflow: hidden !important; margin-top: -2px !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<script>
function copyCode(id) {
    const el = document.getElementById(id);
    if (!el) return;
    navigator.clipboard.writeText(el.innerText).then(() => {
        const btn = document.querySelector('[data-copy="'+id+'"]');
        if(btn){ btn.innerText='✅ Copied!'; setTimeout(()=>{ btn.innerText='📋 Copy'; },1800); }
    });
}
function setRememberCookie(u,p){
    const val = encodeURIComponent(JSON.stringify({username:u,password:p}));
    document.cookie = 'chatbot_rm='+val+'; max-age='+(30*24*3600)+'; path=/';
}
function clearRememberCookie(){
    document.cookie = 'chatbot_rm=; max-age=0; path=/';
}
</script>
""", unsafe_allow_html=True)

# ── FIX 1 + FIX 3: NAME & SUBTITLE ──
defaults = {
    "logged_in": False, "username": "", "user_role": "user",
    "chat_history": [], "voice_text": "",
    "pdf_text": "", "file_content": "",
    "show_upload_popup": False, "inline_upload_type": None,
    "inline_pdf_text": "", "inline_pdf_name": "",
    "inline_file_content": "", "inline_file_name": "",
    "inline_image_b64": "", "inline_image_name": "",
    "current_session_id": None, "active_page": "chat",
    "branding": {"name": "SmartBot AI", "subtitle": "Your 24/7 AI Assistant"},
    "reset_token_input": "",
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

def clear_inline_file():
    for k in ["inline_pdf_text","inline_pdf_name","inline_file_content",
              "inline_file_name","inline_image_b64","inline_image_name"]:
        st.session_state[k] = ""
    st.session_state.inline_upload_type = None
    st.session_state.show_upload_popup  = False

def has_inline_file():
    return bool(st.session_state.inline_pdf_name or
                st.session_state.inline_file_name or
                st.session_state.inline_image_name)

def inline_icon():
    t = st.session_state.inline_upload_type
    return "🖼️" if t == "image" else "📄" if t == "pdf" else "📊"

def inline_name():
    return (st.session_state.inline_pdf_name or
            st.session_state.inline_file_name or
            st.session_state.inline_image_name)

def highlight_code(code: str, lang: str = "") -> str:
    lang = lang.lower().strip()
    h = code.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
    if lang in ("python","py",""):
        h = re.sub(r'(#[^\n]*)', r'<span class="cmt">\1</span>', h)
        h = re.sub(r'("""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\'|"[^"\n]*"|\'[^\'\n]*\')',
                   r'<span class="str">\1</span>', h)
        kws = r'\b(def|class|import|from|return|if|elif|else|for|while|in|not|and|or|is|None|True|False|try|except|finally|with|as|pass|break|continue|lambda|yield|raise|del|global|nonlocal|assert|async|await)\b'
        h = re.sub(kws, r'<span class="kw">\1</span>', h)
        h = re.sub(r'\b([a-zA-Z_]\w*)\s*(?=\()', r'<span class="fn2">\1</span>', h)
        h = re.sub(r'\b(\d+\.?\d*)\b', r'<span class="num">\1</span>', h)
    elif lang in ("js","javascript","ts","typescript"):
        h = re.sub(r'(//[^\n]*)', r'<span class="cmt">\1</span>', h)
        h = re.sub(r'("(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\'|`(?:[^`\\]|\\.)*`)',
                   r'<span class="str">\1</span>', h)
        kws = r'\b(const|let|var|function|return|if|else|for|while|class|import|export|from|default|new|this|typeof|instanceof|async|await|try|catch|finally|throw|null|undefined|true|false|of|in)\b'
        h = re.sub(kws, r'<span class="kw">\1</span>', h)
        h = re.sub(r'\b([a-zA-Z_]\w*)\s*(?=\()', r'<span class="fn2">\1</span>', h)
        h = re.sub(r'\b(\d+\.?\d*)\b', r'<span class="num">\1</span>', h)
    elif lang in ("bash","sh","shell"):
        h = re.sub(r'(#[^\n]*)', r'<span class="cmt">\1</span>', h)
        h = re.sub(r'("(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\')',
                   r'<span class="str">\1</span>', h)
        kws = r'\b(echo|cd|ls|mkdir|rm|cp|mv|cat|grep|sed|awk|chmod|sudo|apt|pip|python|python3|git|docker|npm|yarn)\b'
        h = re.sub(kws, r'<span class="kw">\1</span>', h)
    return h

def render_message_with_code(content: str, msg_index: int):
    pattern = re.compile(r'```(\w*)\n?([\s\S]*?)```', re.MULTILINE)
    last = 0
    block_num = 0
    for m in pattern.finditer(content):
        if m.start() > last:
            st.markdown(content[last:m.start()])
        lang = m.group(1) or "python"
        code = m.group(2)
        highlighted = highlight_code(code, lang)
        block_id = f"cb_{msg_index}_{block_num}"
        block_num += 1
        st.markdown(f"""<div class="code-wrapper">
  <div class="code-header">
    <span style="color:rgba(255,255,255,0.55);">{lang or 'code'}</span>
    <button class="copy-btn" data-copy="{block_id}" onclick="copyCode('{block_id}')">📋 Copy</button>
  </div>
  <div class="code-block" id="{block_id}">{highlighted}</div>
</div>""", unsafe_allow_html=True)
        last = m.end()
    if last < len(content):
        st.markdown(content[last:])

query_params = st.query_params
if "reset_token" in query_params and not st.session_state.logged_in:
    st.session_state.reset_token_input = query_params["reset_token"]

# ══════════════════════════════════════════════════════════
#  AUTH PAGE
# ══════════════════════════════════════════════════════════
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # ── FIX 1: SmartBot AI on login page ──
        st.markdown("""
            <div style='text-align:center;padding:40px 0 30px 0;'>
                <div style='width:60px;height:60px;background:linear-gradient(135deg,#7c3aed,#4f46e5);
                    border-radius:50%;display:flex;align-items:center;justify-content:center;
                    font-size:30px;margin:0 auto 16px auto;'>🤖</div>
                <h1 style='font-size:28px;font-weight:700;margin:0;
                    background:linear-gradient(90deg,#a78bfa,#818cf8);
                    -webkit-background-clip:text;-webkit-text-fill-color:transparent;'>SmartBot AI</h1>
                <p style='color:rgba(255,255,255,0.5);margin-top:8px;font-size:14px;'>Your 24/7 AI Assistant</p>
            </div>
        """, unsafe_allow_html=True)

        if st.session_state.reset_token_input:
            st.markdown("### 🔐 Reset Your Password")
            username_from_token, msg = verify_reset_token(st.session_state.reset_token_input)
            if username_from_token:
                new_pw      = st.text_input("New Password", type="password", key="new_pw_reset")
                confirm_pw  = st.text_input("Confirm Password", type="password", key="confirm_pw_reset")
                if st.button("Set New Password →"):
                    if new_pw and confirm_pw:
                        if new_pw == confirm_pw:
                            if len(new_pw) < 6:
                                st.error("❌ Password must be at least 6 characters!")
                            else:
                                ok, rmsg = reset_password(st.session_state.reset_token_input, new_pw)
                                if ok:
                                    st.success("✅ Password reset! Please login.")
                                    st.session_state.reset_token_input = ""
                                    st.query_params.clear()
                                    st.rerun()
                                else:
                                    st.error(f"❌ {rmsg}")
                        else:
                            st.error("❌ Passwords do not match!")
                    else:
                        st.warning("Please fill all fields.")
            else:
                st.error(f"❌ {msg}")
        else:
            tab1, tab2, tab3 = st.tabs(["🔐  Login", "📝  Register", "🔑  Forgot Password"])

            with tab1:
                st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
                username = st.text_input("Username", placeholder="Username", key="login_user", label_visibility="collapsed")
                password = st.text_input("Password", placeholder="Password", type="password", key="login_pass", label_visibility="collapsed")
                remember_me = st.checkbox("🔒 Remember Me for 30 days")
                st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
                if st.button("Login →", key="login_btn"):
                    if username and password:
                        success, role_or_msg = login_user(username, password)
                        if success:
                            st.session_state.logged_in  = True
                            st.session_state.username   = username
                            st.session_state.user_role  = role_or_msg
                            sessions = get_sessions(username)
                            if sessions:
                                st.session_state.current_session_id = sessions[0]["id"]
                                st.session_state.chat_history = load_history(username, sessions[0]["id"])
                            else:
                                sid = create_session(username)
                                st.session_state.current_session_id = sid
                                st.session_state.chat_history = []
                            if remember_me:
                                st.markdown(f"<script>setRememberCookie('{username}','{password}');</script>",
                                            unsafe_allow_html=True)
                            st.rerun()
                        else:
                            st.error(f"❌ {role_or_msg}")
                    else:
                        st.warning("Please fill in all fields!")

            with tab2:
                st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
                new_username     = st.text_input("Full Name", placeholder="Full Name", key="reg_user", label_visibility="collapsed")
                new_email        = st.text_input("Email Address", placeholder="Email Address", key="reg_email", label_visibility="collapsed")
                new_password     = st.text_input("Create Password", placeholder="Create Password (min 6 chars)", type="password", key="reg_pass", label_visibility="collapsed")
                confirm_password = st.text_input("Confirm Password", placeholder="Confirm Password", type="password", key="reg_confirm", label_visibility="collapsed")
                if st.button("Create Account →", key="reg_btn"):
                    if new_username and new_email and new_password and confirm_password:
                        if new_password == confirm_password:
                            if len(new_password) < 6:
                                st.error("❌ Password must be at least 6 characters!")
                            elif "@" not in new_email:
                                st.error("❌ Please enter a valid email!")
                            else:
                                success, msg = register_user(new_username, new_email, new_password)
                                if success: st.success("✅ Account created! Please login.")
                                else:       st.error(f"❌ {msg}")
                        else:
                            st.error("❌ Passwords do not match!")
                    else:
                        st.warning("Please fill in all fields!")

            with tab3:
                st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
                reset_email = st.text_input("Email", placeholder="Enter your registered email", key="reset_email", label_visibility="collapsed")
                if st.button("Send Reset Link →", key="reset_btn"):
                    if reset_email and "@" in reset_email:
                        ok, msg = request_password_reset(reset_email)
                        if ok: st.success(f"✅ {msg}")
                        else:  st.error(f"❌ {msg}")
                    else:
                        st.warning("Enter a valid email address.")

# ══════════════════════════════════════════════════════════
#  MAIN CHATBOT
# ══════════════════════════════════════════════════════════
else:
    is_admin = st.session_state.user_role == "admin"

    with st.sidebar:
        # ── FIX 3: NO "Powered by Groq + ElevenLabs" ──
        st.markdown(f"""
            <div style='padding:20px 0;border-bottom:1px solid rgba(255,255,255,0.08);margin-bottom:16px;'>
                <div style='display:flex;align-items:center;gap:12px;'>
                    <div style='width:45px;height:45px;background:linear-gradient(135deg,#7c3aed,#4f46e5);
                        border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:22px;'>
                        {"👑" if is_admin else "🤖"}
                    </div>
                    <div>
                        <div style='font-weight:700;font-size:16px;'>{st.session_state.branding['name']}</div>
                        <div style='font-size:11px;color:rgba(255,255,255,0.5);'>{st.session_state.branding['subtitle']}</div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""<div style='background:rgba(124,58,237,0.15);border-radius:10px;padding:8px 12px;font-size:13px;margin-bottom:4px;'>
            {"👑 Admin" if is_admin else "👤"} {st.session_state.username}
        </div>""", unsafe_allow_html=True)

        allowed, remaining = check_rate_limit(st.session_state.username)
        st.markdown(f"""<div style='background:rgba(255,255,255,0.05);border-radius:10px;padding:6px 12px;font-size:12px;margin-bottom:12px;'>
            💬 {remaining}/30 messages left this hour
        </div>""", unsafe_allow_html=True)

        chat_active    = st.session_state.active_page == "chat"
        profile_active = st.session_state.active_page == "profile"
        st.markdown(f"""
        <div style="display:flex;gap:8px;margin-bottom:4px;">
            <div style="flex:1;text-align:center;
                background:{'linear-gradient(90deg,#7c3aed,#4f46e5)' if chat_active else 'rgba(255,255,255,0.06)'};
                border:1px solid {'#7c3aed' if chat_active else 'rgba(255,255,255,0.12)'};
                border-radius:20px;padding:6px 0;font-size:13px;font-weight:600;">
                💬 Chat
            </div>
            <div style="flex:1;text-align:center;
                background:{'linear-gradient(90deg,#7c3aed,#4f46e5)' if profile_active else 'rgba(255,255,255,0.06)'};
                border:1px solid {'#7c3aed' if profile_active else 'rgba(255,255,255,0.12)'};
                border-radius:20px;padding:6px 0;font-size:13px;font-weight:600;">
                👤 Profile
            </div>
        </div>
        """, unsafe_allow_html=True)
        nav1, nav2 = st.columns(2)
        with nav1:
            if st.button("💬", key="nav_chat", help="Chat"):
                st.session_state.active_page = "chat"; st.rerun()
        with nav2:
            if st.button("👤", key="nav_profile", help="Profile"):
                st.session_state.active_page = "profile"; st.rerun()

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        st.markdown("### 💬 Conversations")
        if st.button("➕ New Chat"):
            sid = create_session(st.session_state.username)
            st.session_state.current_session_id = sid
            st.session_state.chat_history = []
            st.rerun()

        sessions = get_sessions(st.session_state.username)
        for s in sessions[:8]:
            is_active = s["id"] == st.session_state.current_session_id
            col_s, col_d = st.columns([4, 1])
            with col_s:
                if st.button(f"{'▶ ' if is_active else ''}{s['name'][:22]}", key=f"sess_{s['id']}"):
                    st.session_state.current_session_id = s["id"]
                    st.session_state.chat_history = load_history(st.session_state.username, s["id"])
                    st.rerun()
            with col_d:
                if st.button("🗑", key=f"del_sess_{s['id']}"):
                    delete_session(s["id"])
                    if st.session_state.current_session_id == s["id"]:
                        st.session_state.current_session_id = None
                        st.session_state.chat_history = []
                    st.rerun()

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        st.markdown("### ⚙️ Settings")
        voice_output = st.toggle("🔊 Voice Output (TTS)", value=False)
        web_search   = st.toggle("🌐 Web Search", value=False)
        image_gen    = st.toggle("🎨 Image Generation", value=False)
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

        st.markdown("### 🌍 Language")
        language = st.selectbox("Response Language:", [
            "English","Hindi","Telugu","Tamil","Spanish","French","German","Arabic"
        ])
        lang_codes = {"English":"en","Hindi":"hi","Telugu":"te","Tamil":"ta",
                      "Spanish":"es","French":"fr","German":"de","Arabic":"ar"}
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

        st.markdown("### 📎 File Upload")
        file_tab = st.radio("Type:", ["PDF","CSV / TXT"], horizontal=True, label_visibility="collapsed")
        if file_tab == "PDF":
            uploaded_pdf = st.file_uploader("Upload PDF", type=["pdf"])
            if uploaded_pdf:
                with st.spinner("Reading PDF..."):
                    doc = fitz.open(stream=uploaded_pdf.read(), filetype="pdf")
                    st.session_state.pdf_text = "".join([p.get_text() for p in doc])[:6000]
                    st.success(f"✅ {len(doc)} pages loaded!")
            if st.session_state.pdf_text and st.button("❌ Remove PDF"):
                st.session_state.pdf_text = ""; st.rerun()
        else:
            uploaded_file = st.file_uploader("Upload CSV or TXT", type=["csv","txt"])
            if uploaded_file:
                with st.spinner("Reading file..."):
                    if uploaded_file.name.endswith(".csv"):
                        df = pd.read_csv(uploaded_file)
                        st.session_state.file_content = f"CSV Data ({df.shape[0]} rows, {df.shape[1]} cols):\n{df.head(50).to_string()}"
                    else:
                        st.session_state.file_content = uploaded_file.read().decode("utf-8", errors="ignore")[:6000]
                    st.success("✅ File loaded!")
            if st.session_state.file_content and st.button("❌ Remove File"):
                st.session_state.file_content = ""; st.rerun()

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        st.markdown("### 🎤 Voice Input")
        # streamlit-mic-recorder based voice input
        try:
            from streamlit_mic_recorder import mic_recorder
            audio = mic_recorder(
                start_prompt="🎤 Speak Now",
                stop_prompt="⏹ Stop",
                just_once=True,
                use_container_width=True,
                key="mic"
            )
            if audio and audio.get("text"):
                st.session_state.voice_text = audio["text"]
                st.success(f"✅ {audio['text']}")
                st.rerun()
            elif audio and audio.get("bytes"):
                # Transcribe with Groq Whisper
                with st.spinner("Transcribing..."):
                    import io
                    audio_bytes = audio["bytes"]
                    transcription = groq_client.audio.transcriptions.create(
                        file=("audio.wav", io.BytesIO(audio_bytes)),
                        model="whisper-large-v3-turbo",
                        language="en"
                    )
                    text = transcription.text
                    if text:
                        st.session_state.voice_text = text
                        st.success(f"✅ {text}")
                        st.rerun()
        except ImportError:
            st.info("🎤 Voice input: add streamlit-mic-recorder to requirements.txt")

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        st.markdown("### 🧠 Personality")
        personality = st.selectbox("Choose:", [
            "Helpful Assistant","Friendly Tutor","Code Expert","Creative Writer","Data Scientist"
        ])
        personality_prompts = {
            "Helpful Assistant": "You are a helpful, smart and friendly AI assistant.",
            "Friendly Tutor":    "You are a friendly tutor who explains things simply with examples.",
            "Code Expert":       "You are an expert programmer. Provide clean, well-commented code with syntax highlighting.",
            "Creative Writer":   "You are a creative writer with a flair for vivid storytelling.",
            "Data Scientist":    "You are an expert data scientist. Provide Python/Pandas code for data analysis.",
        }
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

        st.markdown("### 🎨 Custom Branding")
        new_name     = st.text_input("Bot Name", value=st.session_state.branding["name"])
        new_subtitle = st.text_input("Subtitle",  value=st.session_state.branding["subtitle"])
        if st.button("✅ Apply Branding"):
            st.session_state.branding = {"name": new_name, "subtitle": new_subtitle}; st.rerun()
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

        st.markdown("### 💾 Export Chat")
        export_text = export_history_text(st.session_state.username, st.session_state.current_session_id)
        st.download_button(
            label="⬇️ Download as TXT", data=export_text,
            file_name=f"chat_{st.session_state.username}.txt", mime="text/plain"
        )
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Clear"):
                clear_history(st.session_state.username, st.session_state.current_session_id)
                st.session_state.chat_history = []; st.rerun()
        with col2:
            if st.button("🚪 Logout"):
                st.markdown("<script>clearRememberCookie();</script>", unsafe_allow_html=True)
                for key in ["logged_in","username","user_role","chat_history","pdf_text","file_content","voice_text"]:
                    st.session_state[key] = False if key=="logged_in" else "" if key!="chat_history" else []
                st.session_state.current_session_id = None
                clear_inline_file(); st.rerun()

    # ════════════════════════════════════════════════════
    #  PROFILE PAGE
    # ════════════════════════════════════════════════════
    if st.session_state.active_page == "profile":
        st.markdown("""<h2 style='background:linear-gradient(90deg,#a78bfa,#818cf8);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;
            font-size:26px;font-weight:700;margin-bottom:20px;'>👤 My Profile</h2>""",
            unsafe_allow_html=True)

        user_info     = get_user_info(st.session_state.username)
        all_sessions  = get_sessions(st.session_state.username)
        total_msgs    = sum(s["msg_count"] for s in all_sessions)
        tokens_month  = get_token_usage(st.session_state.username, days=30)
        join_date     = user_info["created_at"][:10] if user_info and user_info.get("created_at") else "N/A"

        st.markdown(f"""
        <div class="profile-card" style="text-align:center;">
            <div class="profile-avatar">{"👑" if is_admin else "🧑"}</div>
            <div style="font-size:22px;font-weight:700;">{st.session_state.username}</div>
            <div style="font-size:13px;color:rgba(255,255,255,0.5);margin-top:4px;">{user_info['email'] if user_info else ''}</div>
            <div style="margin-top:10px;"><span class="feature-badge">{"👑 Admin" if is_admin else "👤 User"}</span></div>
            <div class="stat-grid">
                <div class="stat-item"><div class="stat-num">{total_msgs}</div><div class="stat-lbl">Messages Sent</div></div>
                <div class="stat-item"><div class="stat-num">{len(all_sessions)}</div><div class="stat-lbl">Chat Sessions</div></div>
                <div class="stat-item"><div class="stat-num">{tokens_month:,}</div><div class="stat-lbl">Tokens (30d)</div></div>
            </div>
            <div style="margin-top:16px;font-size:12px;color:rgba(255,255,255,0.35);">📅 Member since {join_date}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("#### 🗂️ Recent Sessions")
        for s in all_sessions[:5]:
            st.markdown(f"""
            <div style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);
                border-radius:10px;padding:10px 16px;margin-bottom:6px;
                display:flex;justify-content:space-between;align-items:center;">
                <span style="font-weight:600;">{s['name']}</span>
                <span style="font-size:12px;color:rgba(255,255,255,0.4);">
                    💬 {s['msg_count']} msgs &nbsp;·&nbsp; {s['created_at'][:10]}
                </span>
            </div>""", unsafe_allow_html=True)

        if st.button("← Back to Chat"):
            st.session_state.active_page = "chat"; st.rerun()
        st.stop()

    # ════════════════════════════════════════════════════
    #  CHAT PAGE
    # ════════════════════════════════════════════════════
    st.markdown(f"""
        <div style='text-align:center;padding:16px 0 24px 0;'>
            <h2 style='background:linear-gradient(90deg,#a78bfa,#818cf8);
                       -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                       font-size:30px;font-weight:700;margin-bottom:12px;'>
                🤖 {st.session_state.branding['name']}
            </h2>
            <div>
                <span class='feature-badge'>⚡ Fast AI</span>
                <span class='feature-badge'>🔊 Voice Output</span>
                <span class='feature-badge'>🌐 Web Search</span>
                <span class='feature-badge'>📄 PDF Chat</span>
                <span class='feature-badge'>🌍 Multi-Language</span>
                <span class='feature-badge'>🎨 Image Gen</span>
                <span class='feature-badge'>📊 Data Analysis</span>
                <span class='feature-badge'>🖼️ Vision</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    if is_admin:
        with st.expander("👑 Admin Panel", expanded=False):
            admin_tab1, admin_tab2 = st.tabs(["👥 Users","📊 Stats"])
            with admin_tab1:
                users = get_all_users()
                for u in users:
                    c1,c2,c3,c4 = st.columns([2,2,1,1])
                    with c1: st.write(f"**{u['username']}**")
                    with c2: st.write(u['email'])
                    with c3: st.write(f"💬 {u['msg_count']}")
                    with c4:
                        new_role = "user" if u["role"]=="admin" else "admin"
                        if st.button(f"Make {new_role}", key=f"role_{u['username']}"):
                            change_user_role(u["username"], new_role); st.rerun()
            with admin_tab2:
                users = get_all_users()
                total_msgs_all = sum(u["msg_count"] for u in users)
                st.markdown(f"""
                <div style='display:grid;grid-template-columns:repeat(3,1fr);gap:12px;'>
                    <div class='stat-card'><div style='font-size:24px;font-weight:700;color:#a78bfa;'>{len(users)}</div><div style='font-size:12px;opacity:0.6;'>Total Users</div></div>
                    <div class='stat-card'><div style='font-size:24px;font-weight:700;color:#a78bfa;'>{total_msgs_all}</div><div style='font-size:12px;opacity:0.6;'>Total Messages</div></div>
                    <div class='stat-card'><div style='font-size:24px;font-weight:700;color:#a78bfa;'>{get_token_usage("admin",days=30)}</div><div style='font-size:12px;opacity:0.6;'>Tokens (30d)</div></div>
                </div>""", unsafe_allow_html=True)

    st.markdown("**⚡ Quick Prompts:**")
    prompts = ["Summarize this","Explain simply","Write code for","Analyze this data","Translate to Hindi","Give me ideas for"]
    cols = st.columns(len(prompts))
    for i, p in enumerate(prompts):
        with cols[i]:
            if st.button(p, key=f"prompt_{i}"): st.session_state.voice_text = p + " "

    if st.session_state.pdf_text:
        st.markdown('<div class="ctx-banner ctx-pdf">📄 <b>PDF loaded</b> — ask me anything about it!</div>', unsafe_allow_html=True)
    if st.session_state.file_content:
        st.markdown('<div class="ctx-banner ctx-file">📊 <b>File loaded</b> — ask me to analyze it!</div>', unsafe_allow_html=True)
    if st.session_state.inline_pdf_name:
        st.markdown(f'<div class="ctx-banner ctx-pdf">📄 <b>{st.session_state.inline_pdf_name}</b> attached</div>', unsafe_allow_html=True)
    if st.session_state.inline_file_name:
        st.markdown(f'<div class="ctx-banner ctx-file">📊 <b>{st.session_state.inline_file_name}</b> attached</div>', unsafe_allow_html=True)
    if st.session_state.inline_image_name:
        st.markdown(f'<div class="ctx-banner ctx-img">🖼️ <b>{st.session_state.inline_image_name}</b> attached</div>', unsafe_allow_html=True)

    tokens_used = get_token_usage(st.session_state.username)
    st.caption(f"🔢 Tokens used this month: **{tokens_used:,}**")

    def search_web(query):
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=3))
                return "Web results:\n\n" + "\n\n".join(
                    [f"{i+1}. {r['title']}\n{r['body']}" for i,r in enumerate(results)]
                ) if results else "No results found."
        except Exception as e:
            return f"Search failed: {e}"

    def translate_text(text, target_lang):
        if target_lang == "en": return text
        try: return GoogleTranslator(source="auto", target=target_lang).translate(text)
        except: return text

    def speak_text(text):
        # Try gTTS first (free, works on cloud)
        try:
            from gtts import gTTS
            tts = gTTS(text=text[:500], lang="en", slow=False)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
                tts.save(tmp.name)
            with open(tmp.name, "rb") as f:
                st.audio(f.read(), format="audio/mp3", autoplay=True)
            os.unlink(tmp.name)
            return
        except:
            pass
        # Fallback: ElevenLabs (works locally)
        try:
            audio = eleven_client.text_to_speech.convert(
                voice_id="JBFqnCBsd6RMkjVDRZzb", text=text[:500], model_id="eleven_turbo_v2_5"
            )
            audio_bytes = b"".join(audio)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
                tmp.write(audio_bytes)
            with open(tmp.name, "rb") as f:
                st.audio(f.read(), format="audio/mp3", autoplay=True)
            os.unlink(tmp.name)
        except:
            st.caption("🔊 Voice available in full deployment")

    def generate_image_free(prompt):
        import urllib.parse
        clean = prompt.strip()
        for kw in ["generate","create","draw","make","show me","give me","an image of","a picture of"]:
            clean = clean.lower().replace(kw, "").strip()
        clean = (clean or prompt).strip()

        # Method 1: Pollinations turbo (fastest ~5-10s)
        try:
            encoded = urllib.parse.quote(clean)
            seed = abs(hash(prompt)) % 9999
            url = f"https://image.pollinations.ai/prompt/{encoded}?width=512&height=512&nologo=true&seed={seed}&model=turbo"
            res = requests.get(url, timeout=30)
            if res.status_code == 200 and len(res.content) > 3000:
                return res.content
        except:
            pass

        # Method 2: Pollinations default (fast fallback)
        try:
            encoded = urllib.parse.quote(clean)
            url = f"https://image.pollinations.ai/prompt/{encoded}?width=512&height=512&nologo=true&seed=42"
            res = requests.get(url, timeout=45)
            if res.status_code == 200 and len(res.content) > 3000:
                return res.content
        except:
            pass

        # Method 3: Pollinations flux (slower but high quality)
        try:
            encoded = urllib.parse.quote(clean)
            url = f"https://image.pollinations.ai/prompt/{encoded}?width=512&height=512&nologo=true&model=flux"
            res = requests.get(url, timeout=60)
            if res.status_code == 200 and len(res.content) > 3000:
                return res.content
        except:
            pass

        return None

    def describe_image_with_groq(b64_image: str, user_question: str) -> str:
        try:
            resp = groq_client.chat.completions.create(
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                messages=[{"role":"user","content":[
                    {"type":"image_url","image_url":{"url":f"data:image/jpeg;base64,{b64_image}"}},
                    {"type":"text","text": user_question or "Describe this image in detail."}
                ]}],
                max_tokens=1024
            )
            return resp.choices[0].message.content
        except Exception as e:
            return f"Image analysis error: {e}"

    for i, chat in enumerate(st.session_state.chat_history):
        with st.chat_message(chat["role"]):
            render_message_with_code(chat["content"], i)
            if chat["role"] == "assistant" and "id" in chat:
                r1, r2, _ = st.columns([1,1,8])
                with r1:
                    if st.button("👍", key=f"up_{i}"):
                        save_reaction(st.session_state.username, chat["id"], "thumbs_up"); st.toast("Thanks! 👍")
                with r2:
                    if st.button("👎", key=f"down_{i}"):
                        save_reaction(st.session_state.username, chat["id"], "thumbs_down"); st.toast("Thanks! 👎")

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    plus_col, options_col = st.columns([1, 11])

    with plus_col:
        st.markdown('<div class="plus-btn">', unsafe_allow_html=True)
        if st.button("＋", key="toggle_popup"):
            st.session_state.show_upload_popup = not st.session_state.show_upload_popup
            if st.session_state.show_upload_popup:
                st.session_state.inline_upload_type = None
        st.markdown('</div>', unsafe_allow_html=True)

    with options_col:
        if st.session_state.show_upload_popup and not has_inline_file():
            st.markdown("<span style='font-size:13px;color:rgba(255,255,255,0.6);'>Attach:</span>", unsafe_allow_html=True)
            pc1, pc2, pc3, _ = st.columns([2, 2, 2, 6])
            with pc1:
                st.markdown('<div class="popup-btn">', unsafe_allow_html=True)
                if st.button("🖼️ Image", key="pick_img"): st.session_state.inline_upload_type = "image"
                st.markdown('</div>', unsafe_allow_html=True)
            with pc2:
                st.markdown('<div class="popup-btn">', unsafe_allow_html=True)
                if st.button("📄 PDF", key="pick_pdf"): st.session_state.inline_upload_type = "pdf"
                st.markdown('</div>', unsafe_allow_html=True)
            with pc3:
                st.markdown('<div class="popup-btn">', unsafe_allow_html=True)
                if st.button("📊 CSV/TXT", key="pick_csv"): st.session_state.inline_upload_type = "csvtxt"
                st.markdown('</div>', unsafe_allow_html=True)

        if st.session_state.inline_upload_type == "image" and not has_inline_file():
            upl = st.file_uploader("Attach image", type=["png","jpg","jpeg","webp"], key="iup_img")
            if upl:
                raw = upl.read()
                st.session_state.inline_image_b64   = base64.b64encode(raw).decode()
                st.session_state.inline_image_name  = upl.name
                st.session_state.inline_upload_type = "image"
                st.session_state.show_upload_popup  = False
                st.rerun()

        elif st.session_state.inline_upload_type == "pdf" and not has_inline_file():
            upl = st.file_uploader("Attach PDF", type=["pdf"], key="iup_pdf")
            if upl:
                with st.spinner("Reading PDF..."):
                    doc = fitz.open(stream=upl.read(), filetype="pdf")
                    st.session_state.inline_pdf_text = "".join([p.get_text() for p in doc])[:6000]
                    st.session_state.inline_pdf_name = upl.name
                st.session_state.inline_upload_type = "pdf"
                st.session_state.show_upload_popup  = False
                st.rerun()

        elif st.session_state.inline_upload_type == "csvtxt" and not has_inline_file():
            upl = st.file_uploader("Attach CSV or TXT", type=["csv","txt"], key="iup_csv")
            if upl:
                with st.spinner("Reading file..."):
                    if upl.name.endswith(".csv"):
                        df = pd.read_csv(upl)
                        st.session_state.inline_file_content = f"CSV ({df.shape[0]} rows × {df.shape[1]} cols):\n{df.head(50).to_string()}"
                    else:
                        st.session_state.inline_file_content = upl.read().decode("utf-8", errors="ignore")[:6000]
                    st.session_state.inline_file_name = upl.name
                st.session_state.inline_upload_type = "csvtxt"
                st.session_state.show_upload_popup  = False
                st.rerun()

        if has_inline_file():
            badge_col, rm_col = st.columns([10, 1])
            with badge_col:
                st.markdown(f"""<div class="file-badge">
                    <span>{inline_icon()}</span>
                    <span class="fn">{inline_name()}</span>
                    <span class="st">· Ready to send</span>
                </div>""", unsafe_allow_html=True)
            with rm_col:
                st.markdown('<div class="remove-badge-btn">', unsafe_allow_html=True)
                if st.button("✕", key="rm_inline"):
                    clear_inline_file(); st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

    user_input = st.session_state.voice_text or st.chat_input("💬 Type your message...")
    if st.session_state.voice_text:
        st.session_state.voice_text = ""

    if user_input:
        allowed, remaining = check_rate_limit(st.session_state.username)
        if not allowed and not is_admin:
            st.error("⏳ Rate limit reached! 30 messages per hour."); st.stop()

        if not st.session_state.current_session_id:
            st.session_state.current_session_id = create_session(st.session_state.username)

        sessions  = get_sessions(st.session_state.username)
        curr_sess = next((s for s in sessions if s["id"]==st.session_state.current_session_id), None)
        if curr_sess and curr_sess["msg_count"] == 0:
            rename_session(st.session_state.current_session_id, user_input[:35])

        with st.chat_message("user"):
            st.markdown(user_input)
            if has_inline_file():
                st.caption(f"{inline_icon()} Attached: **{inline_name()}**")
                if st.session_state.inline_image_b64:
                    img_bytes = base64.b64decode(st.session_state.inline_image_b64)
                    st.image(img_bytes, width=200)

        msg_id = save_message(st.session_state.username, "user", user_input, st.session_state.current_session_id)
        st.session_state.chat_history.append({"role":"user","content":user_input,"id":msg_id})
        record_message_usage(st.session_state.username)

        # ── FIX 4: IMAGE GENERATION ──
        if image_gen:
            with st.chat_message("assistant"):
                with st.spinner("🎨 Generating image... (~10 seconds)"):
                    img_bytes = generate_image_free(user_input)
                if img_bytes:
                    st.image(img_bytes, caption=user_input, use_column_width=True)
                    reply = f"🎨 Generated image for: *{user_input}*"
                    st.success("✅ Done!")
                else:
                    reply = "⚠️ Image generation failed. Please try again!"
                    st.warning(reply)
            msg_id = save_message(st.session_state.username, "assistant", reply, st.session_state.current_session_id)
            st.session_state.chat_history.append({"role":"assistant","content":reply,"id":msg_id})

        elif st.session_state.inline_image_b64:
            with st.chat_message("assistant"):
                with st.spinner("🔍 Analyzing image..."):
                    reply = describe_image_with_groq(st.session_state.inline_image_b64, user_input)
                render_message_with_code(reply, len(st.session_state.chat_history))
                r1, r2, _ = st.columns([1,1,8])
                with r1:
                    if st.button("👍", key="up_img"): st.toast("👍")
                with r2:
                    if st.button("👎", key="dn_img"): st.toast("👎")
            msg_id = save_message(st.session_state.username, "assistant", reply, st.session_state.current_session_id)
            st.session_state.chat_history.append({"role":"assistant","content":reply,"id":msg_id})
            clear_inline_file()

        else:
            system_msg = personality_prompts[personality]
            if st.session_state.pdf_text:
                system_msg += f"\n\nPDF Content:\n{st.session_state.pdf_text}"
            if st.session_state.file_content:
                system_msg += f"\n\nUploaded File:\n{st.session_state.file_content}"
            if st.session_state.inline_pdf_text:
                system_msg += f"\n\nAttached PDF:\n{st.session_state.inline_pdf_text}"
            if st.session_state.inline_file_content:
                system_msg += f"\n\nAttached File:\n{st.session_state.inline_file_content}"
            if web_search:
                system_msg += " Use web search results to give accurate answers."
            if language != "English":
                system_msg += f" Always respond in {language}."

            messages = [{"role":"system","content":system_msg}]
            if web_search:
                with st.spinner("🌐 Searching web..."):
                    search_results = search_web(user_input)
                messages.append({"role":"user","content":f"Web results:\n{search_results}\n\nQuestion: {user_input}"})
            else:
                for chat in st.session_state.chat_history[:-1]:
                    messages.append({"role":chat["role"],"content":chat["content"]})
                messages.append({"role":"user","content":user_input})

            with st.chat_message("assistant"):
                stream_placeholder = st.empty()
                full_reply = ""
                with st.spinner("🤔 Thinking..."):
                    stream = groq_client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=messages,
                        max_tokens=1024,
                        temperature=0.7,
                        stream=True
                    )
                    for chunk in stream:
                        delta = chunk.choices[0].delta.content or ""
                        full_reply += delta
                        stream_placeholder.markdown(full_reply + "▌")

                stream_placeholder.empty()
                reply = full_reply
                render_message_with_code(reply, len(st.session_state.chat_history))
                save_token_usage(st.session_state.username, len(reply)//4 + len(user_input)//4)

                if language != "English":
                    with st.spinner(f"🌍 Translating to {language}..."):
                        reply = translate_text(reply, lang_codes[language])
                    st.markdown(reply)

                if voice_output:
                    with st.spinner("🔊 Generating voice..."):
                        speak_text(reply)

                r1, r2, _ = st.columns([1,1,8])
                with r1:
                    if st.button("👍", key="up_new"): st.toast("Thanks! 👍")
                with r2:
                    if st.button("👎", key="dn_new"): st.toast("Thanks! 👎")

            msg_id = save_message(st.session_state.username, "assistant", reply, st.session_state.current_session_id)
            st.session_state.chat_history.append({"role":"assistant","content":reply,"id":msg_id})
            clear_inline_file()
