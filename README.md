# 🗓️ Smart Scheduler Assistant

> An intelligent multi-agent AI app that reads your Gmail, extracts scheduling requests, and automatically manages your Google Calendar — all through a sleek dark-mode web dashboard.

---

## ✨ Features

- 📧 **Gmail Integration** — Reads and summarises your latest emails
- 📅 **Google Calendar Management** — View, create, update, and delete events
- 🤖 **Multi-Agent AI** — Powered by Groq, Google Gemini, or OpenAI (auto-detected)
- 💬 **Chat Interface** — Natural language scheduling via an interactive AI assistant
- ⚡ **Quick Prompts** — One-click shortcuts for common scheduling tasks
- ☁️ **Cloud-Ready** — Deployed on Streamlit Community Cloud

---

## 🚀 Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure environment
Copy `.env.example` to `.env` and fill in your API key:
```env
GEMINI_API_KEY=your_key_here   # or GROQ_API_KEY / OPENAI_API_KEY
TIMEZONE=Asia/Kolkata
```

### 3. Authenticate with Google
```bash
python authenticate.py
```
This opens a browser to authorise Gmail & Calendar access. A `token.json` file is saved automatically.

### 4. Run the app
```bash
streamlit run app.py
```
Opens at `http://localhost:8501`.

---

## ☁️ Deploying to Streamlit Cloud

1. Push this repo to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io/) → connect your repo → set main file to `app.py`.
3. Add the following under **Settings → Secrets**:

```toml
GEMINI_API_KEY = "your_gemini_api_key"
TIMEZONE = "Asia/Kolkata"

CREDENTIALS_JSON = '''{ ...contents of credentials.json... }'''
TOKEN_JSON = '''{ ...contents of token.json... }'''
```

> **Note:** Regenerate `token.json` by running `python authenticate.py` locally whenever the token expires, then update `TOKEN_JSON` in Streamlit Secrets.

---

## 📂 Project Structure

```
smart-scheduler/
├── .streamlit/
│   └── config.toml        # Theme and server settings
├── app.py                 # Streamlit web app (UI + agent wiring)
├── main.py                # CLI mode entry point
├── authenticate.py        # One-time Google OAuth setup script
├── credentials.json       # Google OAuth client secret (keep private)
├── token.json             # Google OAuth access token (keep private)
├── requirements.txt       # Python dependencies
├── Dockerfile             # Container build manifest
├── Procfile               # Process file for cloud deployment
└── .env                   # Local environment variables
```

---

## 🔑 Supported LLM Providers

The app auto-selects a provider based on which API key is present (in priority order):

| Priority | Provider | Environment Variable | Model Used |
|:---:|---|---|---|
| 1 | **Groq** | `GROQ_API_KEY` | `llama-3.3-70b-versatile` |
| 2 | **Google Gemini** | `GEMINI_API_KEY` | `gemini-2.0-flash` |
| 3 | **OpenAI** | `OPENAI_API_KEY` | `gpt-4o-mini` |

---

## 🔒 Security Notes

- `credentials.json` and `token.json` are listed in `.gitignore` — never commit them.
- Store all secrets in Streamlit Cloud's **Secrets** manager, not in the repository.
- Keep your Google Cloud OAuth app in **Testing** mode and add authorised test users, or publish it to production to remove the 7-day token expiry.
