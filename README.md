# 🤖 My AI Chatbot

A full-stack AI chatbot built from scratch with Python and Streamlit, powered by Groq LLM + ElevenLabs TTS.

---

## ✨ Features

- ⚡ **Groq LLM** — LLaMA 3.3 70B with streaming responses
- 🔊 **ElevenLabs TTS** — Human-like voice output
- 🎤 **Voice Input** — Speak your message using microphone
- 📄 **PDF Chat (RAG)** — Upload PDF and ask questions about it
- 📊 **CSV/TXT Analysis** — Upload data files for analysis
- 🌐 **Web Search** — Real-time DuckDuckGo search integration
- 🌍 **Multi-Language** — 8 languages supported
- 🔐 **Authentication** — Login, Register, Password Reset
- 💬 **Multi-Session Chat** — Create, rename, delete sessions
- 👑 **Admin Panel** — Manage users, roles, and stats
- 👤 **User Profile** — Message count, token usage, sessions
- 🖼️ **Vision** — Upload image and ask questions about it
- 🎨 **Code Highlighting** — Syntax highlighting with copy button
- 📎 **Inline File Upload** — Attach files directly in chat
- 🔒 **Remember Me** — 30-day cookie persistence
- ⏱️ **Rate Limiting** — 30 messages per hour per user
- 🔢 **Token Tracking** — Monthly usage per user

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Streamlit |
| LLM | Groq API (LLaMA 3.3 70B) |
| TTS | ElevenLabs API |
| STT | SpeechRecognition + Google |
| Database | SQLite |
| PDF Parsing | PyMuPDF (fitz) |
| Web Search | DuckDuckGo Search |
| Translation | Deep Translator |
| Auth | bcrypt |

---

## 📁 Project Structure

```
my_chatbot/
├── app.py              # Main Streamlit application
├── auth.py             # Authentication & database logic
├── requirements.txt    # Python dependencies
├── .env                # API keys (never commit this!)
├── .gitignore          # Git ignore rules
└── README.md           # This file
```

---

## ⚙️ Setup & Installation

### 1. Clone the repository
```bash
git clone https://github.com/DhanalaxmiSanapala2005/my-chatbot.git
cd my-chatbot
```

### 2. Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Create `.env` file
```env
GROQ_API_KEY=your_groq_api_key
ELEVENLABS_API_KEY=your_elevenlabs_api_key
HF_API_TOKEN=your_huggingface_token
SMTP_EMAIL=your_email@gmail.com
SMTP_APP_PASSWORD=your_gmail_app_password
```

### 5. Run the app
```bash
streamlit run app.py
```

---

## 🔑 Getting API Keys

| Service | Link | Cost |
|---------|------|------|
| Groq | [console.groq.com](https://console.groq.com) | Free |
| ElevenLabs | [elevenlabs.io](https://elevenlabs.io) | Free tier |
| HuggingFace | [huggingface.co](https://huggingface.co) | Free |

---

## 🌐 Deployment (Streamlit Cloud)

1. Push code to GitHub (**never push `.env`**)
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repository
4. Set **Main file**: `app.py`
5. Go to **Advanced Settings → Secrets** and add:
```toml
GROQ_API_KEY = "your_key"
ELEVENLABS_API_KEY = "your_key"
SMTP_EMAIL = "your_email"
SMTP_APP_PASSWORD = "your_password"
```
6. Click **Deploy!**

---

## 🔒 Security

- Passwords hashed with **bcrypt**
- API keys stored in `.env` — never in code
- `.env` and `chatbot.db` listed in `.gitignore`
- Rate limiting prevents API abuse
- Email-based password reset with expiring tokens

---

## 📸 Screenshots

| Login Page | Chat Page |
|-----------|-----------|
| Dark purple UI with Login/Register tabs | Full chat interface with sidebar |

---

## 🗺️ Roadmap

- [ ] 🌐 Custom domain deployment
- [ ] 💳 Razorpay payment integration
- [ ] 🎨 Image generation
- [ ] 🔒 Multi-tenant architecture
- [ ] 📊 Usage billing per user
- [ ] 🧠 Vector-based RAG with ChromaDB

---

## 👩‍💻 Built By

**Dhanalaxmi Sanapala**
- GitHub: [@DhanalaxmiSanapala2005](https://github.com/DhanalaxmiSanapala2005)

---

## 📄 License

This project is for educational and personal use.
