# 🧠 Smart Scheduler Assistant

> An intelligent multi-agent AI web application that reads your Gmail, extracts schedule requests, and automatically manages your Google Calendar through an interactive dark-mode web dashboard.

---

## 📊 Current Project Setup Status

| Component | Status | Details |
| :--- | :---: | :--- |
| **Workspace & Files** | ✅ **Done** | All project files located in `d:\smart scheduler` |
| **Python Environment** | ✅ **Done** | Python 3.13 configured with Streamlit |
| **Web Dashboard UI** | ✅ **Done** | Streamlit web interface in `app.py` |
| **Multi-LLM Engine** | ✅ **Done** | Connected to **Google Gemini** (`gemini-2.5-flash`) with Groq/OpenAI failover |
| **Google Credentials** | ✅ **Done** | OAuth client secret (`credentials.json`) loaded |
| **Authentication** | ✅ **Done** | Access token (`token.json`) generated |
| **Deployability** | ✅ **Done** | Containerized with `Dockerfile` & `Procfile` |

---

## 🚀 How to Run the Web Dashboard

Launch the interactive web application in your browser:

```powershell
streamlit run app.py
```

*The web dashboard will automatically open at `http://localhost:8501`.*

### 🖥️ CLI Mode (Terminal)
If you prefer the command-line interface:
```powershell
python main.py
```

---

## 🌐 Deploying to Production

### Option 1: Streamlit Community Cloud (Free & Instant)
1. Push your repository to GitHub.
2. Sign in to [share.streamlit.io](https://share.streamlit.io/).
3. Connect your repository, set main file to `app.py`.
4. Add your secrets (`GEMINI_API_KEY` or `GROQ_API_KEY`) under **Advanced Settings > Secrets**.

### Option 2: Docker Containerization
Build and run locally or push to GCP Cloud Run / AWS ECS / Render:

```bash
# Build the Docker image
docker build -t smart-scheduler .

# Run the container
docker run -p 8501:8501 --env-file .env smart-scheduler
```

### Option 3: Render / Cloud Web Services
- Build Command: `pip install -r pyproject.toml`
- Start Command: `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0`

---

## 📂 Project Structure

```text
d:\smart scheduler/
├── .streamlit/
│   └── config.toml        # Dark mode styling and server options
├── app.py                 # Streamlit Web Application UI & Dashboard
├── main.py                # Core multi-agent assistant logic (CLI mode)
├── authenticate.py        # Google OAuth authorization script
├── Dockerfile             # Multi-stage production container manifest
├── Procfile               # Cloud deployment process file (Render/Heroku)
├── credentials.json       # Google OAuth client secret
├── token.json             # Google OAuth access token
├── .env                   # Environment variables (GEMINI_API_KEY, TIMEZONE)
└── README.md              # Project documentation and deployment guide
```
