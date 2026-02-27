import sqlite3
import bcrypt
import smtplib
import secrets
import string
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

DB_PATH = "chatbot.db"
SMTP_EMAIL = os.getenv("SMTP_EMAIL")
SMTP_PASSWORD = os.getenv("SMTP_APP_PASSWORD")
RATE_LIMIT_PER_HOUR = 30

# ─── DB INIT ──────────────────────────────────────────────
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT DEFAULT 'user',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS chat_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        session_name TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS chat_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        session_id INTEGER,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(session_id) REFERENCES chat_sessions(id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS message_reactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        message_id INTEGER NOT NULL,
        reaction TEXT NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS reset_tokens (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        token TEXT UNIQUE NOT NULL,
        expires_at TIMESTAMP NOT NULL,
        used INTEGER DEFAULT 0
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS rate_limits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS token_usage (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        tokens_used INTEGER NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    conn.commit()

    # Add default admin if not exists
    try:
        admin_pass = bcrypt.hashpw("admin123".encode(), bcrypt.gensalt())
        c.execute("INSERT INTO users (username, email, password, role) VALUES (?, ?, ?, ?)",
                  ("admin", "admin@chatbot.ai", admin_pass, "admin"))
        conn.commit()
    except sqlite3.IntegrityError:
        pass

    # ── Make Dhanalaxmi admin automatically ──
    try:
        c.execute("UPDATE users SET role='admin' WHERE username='Dhanalaxmi'")
        conn.commit()
    except:
        pass

    conn.close()


# ─── AUTH ──────────────────────────────────────────────────
def register_user(username, email, password):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        # Auto admin for Dhanalaxmi
        role = 'admin' if username == 'Dhanalaxmi' else 'user'
        c.execute("INSERT INTO users (username, email, password, role) VALUES (?, ?, ?, ?)",
                  (username, email, hashed, role))
        conn.commit()
        conn.close()
        return True, "Account created successfully!"
    except sqlite3.IntegrityError as e:
        if "username" in str(e):
            return False, "Username already exists!"
        return False, "Email already registered!"
    except Exception as e:
        return False, str(e)


def login_user(username, password):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT password, role FROM users WHERE username=?", (username,))
        result = c.fetchone()
        conn.close()
        if result and bcrypt.checkpw(password.encode(), result[0]):
            return True, result[1]
        return False, "Invalid username or password!"
    except Exception as e:
        return False, str(e)


def get_user_info(username):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT username, email, role, created_at FROM users WHERE username=?", (username,))
        result = c.fetchone()
        conn.close()
        if result:
            return {"username": result[0], "email": result[1], "role": result[2], "created_at": result[3]}
        return None
    except Exception:
        return None


def get_all_users():
    """Admin only — list all users with stats."""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""
            SELECT u.username, u.email, u.role, u.created_at,
                   COUNT(ch.id) as msg_count
            FROM users u
            LEFT JOIN chat_history ch ON ch.username = u.username
            GROUP BY u.username
            ORDER BY u.created_at DESC
        """)
        results = c.fetchall()
        conn.close()
        return [{"username": r[0], "email": r[1], "role": r[2],
                 "created_at": r[3], "msg_count": r[4]} for r in results]
    except Exception:
        return []


def change_user_role(username, new_role):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("UPDATE users SET role=? WHERE username=?", (new_role, username))
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False


# ─── RATE LIMITING ─────────────────────────────────────────
def check_rate_limit(username):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        one_hour_ago = datetime.now() - timedelta(hours=1)
        c.execute("SELECT COUNT(*) FROM rate_limits WHERE username=? AND timestamp > ?",
                  (username, one_hour_ago))
        count = c.fetchone()[0]
        conn.close()
        remaining = max(0, RATE_LIMIT_PER_HOUR - count)
        return count < RATE_LIMIT_PER_HOUR, remaining
    except Exception:
        return True, RATE_LIMIT_PER_HOUR


def record_message_usage(username):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT INTO rate_limits (username) VALUES (?)", (username,))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Rate limit record error: {e}")


# ─── TOKEN USAGE ───────────────────────────────────────────
def save_token_usage(username, tokens):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT INTO token_usage (username, tokens_used) VALUES (?, ?)", (username, tokens))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Token save error: {e}")


def get_token_usage(username, days=30):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        since = datetime.now() - timedelta(days=days)
        c.execute("SELECT SUM(tokens_used) FROM token_usage WHERE username=? AND timestamp > ?",
                  (username, since))
        result = c.fetchone()[0]
        conn.close()
        return result or 0
    except Exception:
        return 0


# ─── SESSIONS ──────────────────────────────────────────────
def create_session(username, session_name=None):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        if not session_name:
            session_name = f"Chat {datetime.now().strftime('%b %d %H:%M')}"
        c.execute("INSERT INTO chat_sessions (username, session_name) VALUES (?, ?)",
                  (username, session_name))
        session_id = c.lastrowid
        conn.commit()
        conn.close()
        return session_id
    except Exception as e:
        print(f"Session error: {e}")
        return None


def get_sessions(username):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""
            SELECT s.id, s.session_name, s.created_at, COUNT(ch.id) as msg_count
            FROM chat_sessions s
            LEFT JOIN chat_history ch ON ch.session_id = s.id
            WHERE s.username=?
            GROUP BY s.id
            ORDER BY s.created_at DESC
        """, (username,))
        results = c.fetchall()
        conn.close()
        return [{"id": r[0], "name": r[1], "created_at": r[2], "msg_count": r[3]} for r in results]
    except Exception:
        return []


def rename_session(session_id, new_name):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("UPDATE chat_sessions SET session_name=? WHERE id=?", (new_name, session_id))
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False


def delete_session(session_id):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("DELETE FROM chat_history WHERE session_id=?", (session_id,))
        c.execute("DELETE FROM chat_sessions WHERE id=?", (session_id,))
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False


# ─── CHAT HISTORY ──────────────────────────────────────────
def save_message(username, role, content, session_id=None):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT INTO chat_history (username, session_id, role, content) VALUES (?, ?, ?, ?)",
                  (username, session_id, role, content))
        msg_id = c.lastrowid
        conn.commit()
        conn.close()
        return msg_id
    except Exception as e:
        print(f"Save error: {e}")
        return None


def load_history(username, session_id=None):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        if session_id:
            c.execute("SELECT id, role, content FROM chat_history WHERE username=? AND session_id=? ORDER BY timestamp ASC",
                      (username, session_id))
        else:
            c.execute("SELECT id, role, content FROM chat_history WHERE username=? ORDER BY timestamp ASC",
                      (username,))
        results = c.fetchall()
        conn.close()
        return [{"id": r[0], "role": r[1], "content": r[2]} for r in results]
    except Exception:
        return []


def clear_history(username, session_id=None):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        if session_id:
            c.execute("DELETE FROM chat_history WHERE username=? AND session_id=?", (username, session_id))
        else:
            c.execute("DELETE FROM chat_history WHERE username=?", (username,))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Clear error: {e}")


def export_history_text(username, session_id=None):
    history = load_history(username, session_id)
    lines = [f"Chat Export — {username} — {datetime.now().strftime('%Y-%m-%d %H:%M')}\n{'='*60}\n"]
    for msg in history:
        role = "You" if msg["role"] == "user" else "AI"
        lines.append(f"[{role}]\n{msg['content']}\n")
    return "\n".join(lines)


# ─── REACTIONS ─────────────────────────────────────────────
def save_reaction(username, message_id, reaction):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("DELETE FROM message_reactions WHERE username=? AND message_id=?",
                  (username, message_id))
        c.execute("INSERT INTO message_reactions (username, message_id, reaction) VALUES (?, ?, ?)",
                  (username, message_id, reaction))
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False


# ─── PASSWORD RESET ────────────────────────────────────────
def _generate_token(length=32):
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def request_password_reset(email):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT username FROM users WHERE email=?", (email,))
        result = c.fetchone()
        if not result:
            conn.close()
            return False, "No account found with that email."
        username = result[0]
        token = _generate_token()
        expires_at = datetime.now() + timedelta(hours=1)
        c.execute("INSERT INTO reset_tokens (username, token, expires_at) VALUES (?, ?, ?)",
                  (username, token, expires_at))
        conn.commit()
        conn.close()
        _send_reset_email(email, username, token)
        return True, "Reset link sent to your email!"
    except Exception as e:
        return False, str(e)


def verify_reset_token(token):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT username, expires_at, used FROM reset_tokens WHERE token=?", (token,))
        result = c.fetchone()
        conn.close()
        if not result:
            return None, "Invalid token."
        username, expires_at, used = result
        if used:
            return None, "Token already used."
        if datetime.fromisoformat(expires_at) < datetime.now():
            return None, "Token expired."
        return username, "Valid"
    except Exception as e:
        return None, str(e)


def reset_password(token, new_password):
    username, msg = verify_reset_token(token)
    if not username:
        return False, msg
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        hashed = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt())
        c.execute("UPDATE users SET password=? WHERE username=?", (hashed, username))
        c.execute("UPDATE reset_tokens SET used=1 WHERE token=?", (token,))
        conn.commit()
        conn.close()
        return True, "Password reset successfully!"
    except Exception as e:
        return False, str(e)


def _send_reset_email(to_email, username, token):
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "🔐 Password Reset — SmartBot AI"
        msg["From"] = SMTP_EMAIL
        msg["To"] = to_email
        reset_link = f"https://dhana-smartbot.streamlit.app/?reset_token={token}"
        html = f"""
        <div style="font-family:Inter,sans-serif;max-width:480px;margin:0 auto;
                    background:#0f0c29;color:white;border-radius:16px;padding:32px;">
            <h2 style="color:#a78bfa;">Password Reset — SmartBot AI</h2>
            <p>Hi <b>{username}</b>,</p>
            <p>Click the button below to reset your password. This link expires in <b>1 hour</b>.</p>
            <a href="{reset_link}" style="display:inline-block;background:linear-gradient(90deg,#7c3aed,#4f46e5);
               color:white;padding:12px 24px;border-radius:10px;text-decoration:none;font-weight:600;">
               Reset Password →
            </a>
            <p style="color:rgba(255,255,255,0.4);font-size:12px;margin-top:24px;">
                If you didn't request this, ignore this email.
            </p>
        </div>
        """
        msg.attach(MIMEText(html, "html"))
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.sendmail(SMTP_EMAIL, to_email, msg.as_string())
    except Exception as e:
        print(f"Email error: {e}")
