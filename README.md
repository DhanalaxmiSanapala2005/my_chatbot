🤖 My AI Chatbot

A full-stack AI chatbot built from scratch using Python + Streamlit, powered by Groq LLaMA 3.3 70B and ElevenLabs TTS.

Designed with authentication, admin controls, RAG, voice support, and multi-session chat.

✨ Features

⚡ Groq LLM — LLaMA 3.3 70B with streaming responses

🔊 ElevenLabs TTS — Human-like voice output

🎤 Voice Input — Speak using microphone

📄 PDF Chat (RAG) — Upload PDF and ask questions

📊 CSV/TXT Analysis — Upload data files

🌐 Web Search — Real-time DuckDuckGo integration

🌍 Multi-Language — 8 languages supported

🔐 Authentication — Login, Register, Password Reset

💬 Multi-Session Chat — Create, rename, delete sessions

👑 Admin Panel — Manage users & analytics

👤 User Profile — Token usage & session tracking

🖼️ Vision Support — Upload images and ask questions

🎨 Code Highlighting — Copy-ready formatted code

📎 Inline File Upload

🔒 Remember Me — 30-day cookie persistence

⏱️ Rate Limiting — 30 messages/hour per user

🔢 Token Tracking — Monthly usage monitoring

🛠️ Tech Stack
Layer	Technology
Frontend	Streamlit
LLM	Groq API (LLaMA 3.3 70B)
TTS	ElevenLabs API
STT	SpeechRecognition + Google
Database	SQLite
PDF Parsing	PyMuPDF (fitz)
Web Search	DuckDuckGo Search
Translation	Deep Translator
Authentication	bcrypt
📁 Project Structure
my_chatbot/
├── app.py
├── auth.py
├── requirements.txt
├── .env (local only)
├── .gitignore
└── README.md
⚙️ Setup & Installation
1️⃣ Clone Repository
git clone https://github.com/DhanalaxmiSanapala2005/my_chatbot.git
cd my_chatbot
2️⃣ Create Virtual Environment
python -m venv venv
venv\Scripts\activate       # Windows
source venv/bin/activate    # Mac/Linux
3️⃣ Install Dependencies
pip install -r requirements.txt
4️⃣ Create .env File
GROQ_API_KEY=your_groq_api_key
ELEVENLABS_API_KEY=your_elevenlabs_api_key
HF_API_TOKEN=your_huggingface_token
SMTP_EMAIL=your_email@gmail.com
SMTP_APP_PASSWORD=your_app_password
5️⃣ Run Application
streamlit run app.py
🌐 Deployment (Streamlit Cloud)

Push code to GitHub (never push .env)

Go to https://share.streamlit.io

Connect repository

Set Main file → app.py

Add secrets in Advanced Settings

Click Deploy 🚀

🔒 Security

Passwords hashed with bcrypt

API keys stored securely in .env

.env & database excluded via .gitignore

Rate limiting prevents abuse

Email-based password reset with expiring tokens

🗺️ Roadmap

🌐 Custom domain

💳 Razorpay integration

🎨 Image generation

📊 Usage-based billing

🧠 Vector RAG with ChromaDB

👩‍💻 Author

Dhanalaxmi Sanapala
GitHub: https://github.com/DhanalaxmiSanapala2005

📄 License

For educational and personal use.
