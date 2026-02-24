# 🤖 My AI Chatbot

> A full-stack AI chatbot built using **Python + Streamlit**, powered by **Groq LLaMA 3.3 70B** and **ElevenLabs TTS**.

An AI SaaS-style chatbot with authentication, admin controls, RAG, voice support, and multi-session chat.

---

## 🚀 Features

### 🧠 AI Capabilities
- ⚡ Groq LLM (LLaMA 3.3 70B) with streaming responses  
- 📄 PDF Chat (RAG support)  
- 🖼️ Vision — Upload image & ask questions  
- 🌐 Real-time Web Search (DuckDuckGo)  
- 🌍 Multi-language support (8 languages)  

### 🎙️ Voice & Interaction
- 🎤 Speech-to-Text (Microphone input)  
- 🔊 ElevenLabs Text-to-Speech  
- 📎 Inline file uploads  
- 🎨 Code highlighting with copy button  

### 🔐 Authentication & Security
- Login / Register / Password Reset  
- 🔒 bcrypt password hashing  
- 🔒 Remember Me (30-day cookie session)  
- ⏱️ Rate limiting (30 messages/hour per user)  
- 🔢 Monthly token usage tracking  

### 👑 Admin & User Management
- 👑 Admin dashboard  
- 👤 User profile analytics  
- 💬 Multi-session chat management  
- 📊 Usage statistics per user  

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Streamlit |
| LLM | Groq API (LLaMA 3.3 70B) |
| TTS | ElevenLabs API |
| STT | SpeechRecognition + Google |
| Database | SQLite |
| PDF Parsing | PyMuPDF (fitz) |
| Web Search | DuckDuckGo Search |
| Translation | Deep Translator |
| Authentication | bcrypt |

---

## 📂 Project Structure
my_chatbot/
├── app.py
├── auth.py
├── requirements.txt
├── .env (local only)
├── .gitignore
└── README.md


---

## ⚙️ Setup & Installation

### 1️⃣ Clone Repository
```bash
git clone https://github.com/DhanalaxmiSanapala2005/my_chatbot.git
cd my_chatbot
2️⃣ Create Virtual Environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
3️⃣ Install Dependencies
pip install -r requirements.txt
4️⃣ Create .env File
GROQ_API_KEY=your_groq_api_key
ELEVENLABS_API_KEY=your_elevenlabs_api_key
HF_API_TOKEN=your_huggingface_token
SMTP_EMAIL=your_email@gmail.com
SMTP_APP_PASSWORD=your_app_password
5️⃣ Run the App
streamlit run app.py
🔑 Getting API Keys
Service	Link	Cost
Groq	https://console.groq.com
	Free
ElevenLabs	https://elevenlabs.io
	Free tier
HuggingFace	https://huggingface.co
	Free
🌐 Deployment (Streamlit Cloud)

Push code to GitHub (never push .env)

Go to https://share.streamlit.io

Connect your repository

Set Main file → app.py

Add secrets in Advanced Settings

Click Deploy 🚀

🔒 Security

Passwords hashed with bcrypt

API keys stored securely in .env

.env and chatbot.db excluded via .gitignore

Rate limiting to prevent API abuse

Email-based password reset with expiring tokens

🗺️ Roadmap

🌐 Custom domain deployment

💳 Razorpay payment integration

🎨 AI image generation

🔒 Multi-tenant architecture

📊 Usage-based billing

🧠 Vector-based RAG with ChromaDB

👩‍💻 Built By

Dhanalaxmi Sanapala
GitHub: https://github.com/DhanalaxmiSanapala2005

📄 License

For educational and personal use.
