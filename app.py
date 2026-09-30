import streamlit as st
import os
import sys
import dotenv
from dotenv import load_dotenv

# Page Configuration - MUST be first Streamlit command
st.set_page_config(
    page_title="Smart Scheduler Assistant",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern dark-mode aesthetic
st.markdown("""
<style>
    /* Global Styles */
    .stApp {
        background: linear-gradient(135deg, #0e1117 0%, #161b22 100%);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Header Banner */
    .main-header {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 24px 32px;
        margin-bottom: 24px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    
    .main-title {
        font-size: 1.85rem;
        font-weight: 700;
        background: linear-gradient(90deg, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    
    .subtitle {
        color: #9ca3af;
        font-size: 0.95rem;
        margin-top: 4px;
    }
    
    /* Status Badges */
    .badge {
        display: inline-flex;
        align-items: center;
        padding: 6px 14px;
        border-radius: 9999px;
        font-size: 0.82rem;
        font-weight: 600;
        margin-right: 8px;
    }
    
    .badge-success {
        background: rgba(34, 197, 94, 0.15);
        color: #4ade80;
        border: 1px solid rgba(34, 197, 94, 0.3);
    }
    
    .badge-info {
        background: rgba(99, 102, 241, 0.15);
        color: #818cf8;
        border: 1px solid rgba(99, 102, 241, 0.3);
    }
    
    /* Card Container */
    .custom-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 16px;
        transition: transform 0.2s, border-color 0.2s;
    }
    
    .custom-card:hover {
        border-color: rgba(99, 102, 241, 0.4);
        transform: translateY(-2px);
    }

    /* Sidebar Customization */
    section[data-testid="stSidebar"] {
        background: #11151c;
        border-right: 1px solid rgba(255, 255, 255, 0.06);
    }

    /* Hide Streamlit branding header/footer for cleaner UI */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=unsafe_allow_html if 'unsafe_allow_html' in locals() else True)

load_dotenv()
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import json

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CREDS_PATH = os.path.join(SCRIPT_DIR, "credentials.json")
TOKEN_PATH = os.path.join(SCRIPT_DIR, "token.json")

def sync_google_credentials():
    """Restores credentials.json and token.json from st.secrets if missing on disk (e.g. Streamlit Cloud)."""
    try:
        if not os.path.exists(CREDS_PATH):
            creds_val = None
            if hasattr(st, "secrets"):
                if "CREDENTIALS_JSON" in st.secrets:
                    creds_val = st.secrets["CREDENTIALS_JSON"]
                elif "credentials_json" in st.secrets:
                    creds_val = st.secrets["credentials_json"]
            
            if creds_val:
                content = creds_val if isinstance(creds_val, str) else json.dumps(dict(creds_val))
                with open(CREDS_PATH, "w", encoding="utf-8") as f:
                    f.write(content)

        if not os.path.exists(TOKEN_PATH):
            token_val = None
            if hasattr(st, "secrets"):
                if "TOKEN_JSON" in st.secrets:
                    token_val = st.secrets["TOKEN_JSON"]
                elif "token_json" in st.secrets:
                    token_val = st.secrets["token_json"]
            
            if token_val:
                content = token_val if isinstance(token_val, str) else json.dumps(dict(token_val))
                with open(TOKEN_PATH, "w", encoding="utf-8") as f:
                    f.write(content)
    except Exception as e:
        pass

sync_google_credentials()

# Helper function to initialize agent dynamically
@st.cache_resource(show_spinner=False)
def get_assistant_team():
    try:
        from agno.agent import Agent
        from agno.team import Team
        from agno.tools.google.gmail import GmailTools
        from agno.tools.google.calendar import GoogleCalendarTools
        from agno.db.sqlite import SqliteDb

        def get_secret(key_name, default=None):
            if hasattr(st, "secrets") and key_name in st.secrets:
                return st.secrets[key_name]
            return os.getenv(key_name, default)

        timezone = get_secret("TIMEZONE", "Asia/Kolkata")
        groq_api_key = get_secret("GROQ_API_KEY")
        gemini_api_key = get_secret("GEMINI_API_KEY") or get_secret("GOOGLE_API_KEY")
        openai_api_key = get_secret("OPENAI_API_KEY")
        nebius_api_key = get_secret("NEBIUS_API_KEY")

        provider_name = "Unknown"
        if groq_api_key:
            from agno.models.groq import Groq
            model = Groq(id="llama-3.3-70b-versatile", api_key=groq_api_key)
            provider_name = "Groq (llama-3.3-70b-versatile)"
        elif gemini_api_key:
            from agno.models.google import Gemini
            model = Gemini(id="gemini-2.5-flash", api_key=gemini_api_key)
            provider_name = "Google Gemini (gemini-2.5-flash)"
        elif openai_api_key:
            from agno.models.openai import OpenAIChat
            model = OpenAIChat(id="gpt-4o-mini", api_key=openai_api_key)
            provider_name = "OpenAI (gpt-4o-mini)"
        elif nebius_api_key:
            from agno.models.nebius import Nebius
            model = Nebius(id="Qwen/Qwen3-32b", api_key=nebius_api_key)
            provider_name = "Nebius (Qwen3-32b)"
        else:
            return None, "No API key found in environment."

        DB_PATH = os.getenv("DB_PATH", os.path.join(SCRIPT_DIR, "tmp", "data.db"))
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        db = SqliteDb(db_file=DB_PATH)

        email_agent = Agent(
            model=model,
            markdown=True,
            tools=[GmailTools(credentials_path=CREDS_PATH, token_path=TOKEN_PATH)],
            description="Gmail reading specialist.",
            instructions=[
                "Use tools to search and read emails from Gmail.",
                "Limit email searches/fetches to a maximum of 3-5 latest emails to remain fast.",
                "Focus on extracting key details such as sender, subject, and concise summary of the body.",
                "Never fabricate email content; only use the available information.",
                "If no emails are found, respond with 'No emails found.'",
            ],
            db=db,
            add_history_to_context=True,
            num_history_runs=3,
        )

        calendar_agent = Agent(
            model=model,
            description="Google Calendar specialist.",
            tools=[GoogleCalendarTools(credentials_path=CREDS_PATH, token_path=TOKEN_PATH)],
            instructions=[
                f"""You are a scheduling assistant. Help users:
                - get scheduled events from a certain date/time
                - create events based on details
                - update existing events
                - delete events
                - find available time slots
                - all times in {timezone}"""
            ],
            add_datetime_to_context=True,
            db=db,
            add_history_to_context=True,
            num_history_runs=3,
        )

        team = Team(
            name="Productivity Team",
            members=[email_agent, calendar_agent],
            description="Team to manage Gmail & Google Calendar.",
            model=model,
            instructions=[
                "Analyze user requests:",
                "- If directly about Google Calendar, delegate to calendar_agent.",
                "- If about emails or converting emails into events, use email_agent then calendar_agent.",
                "Ensure all necessary event details (name, date, time) are provided.",
            ],
            db=db,
            add_history_to_context=True,
            num_history_runs=3,
        )

        return (team, provider_name), None
    except Exception as e:
        return (None, None), str(e)

# Sidebar Header & Status
with st.sidebar:
    st.markdown("### ⚙️ System Status")
    
    creds_exist = os.path.exists(CREDS_PATH)
    token_exist = os.path.exists(TOKEN_PATH)
    
    if creds_exist and token_exist:
        st.success("Google OAuth Credentials: **Connected** ✅")
    else:
        st.error("Google OAuth: **Missing Credentials** ❌")
        if not creds_exist:
            st.caption("⚠️ `credentials.json` not found.")
        if not token_exist:
            st.caption("⚠️ `token.json` missing. Run `python authenticate.py`.")

    (assistant_data, err) = get_assistant_team()
    team = None
    if assistant_data and assistant_data[0]:
        team, provider = assistant_data
        st.info(f"LLM Engine: **{provider}**")
    else:
        st.error(f"LLM Error: {err}")

    st.markdown("---")
    st.markdown("### ⚡ Quick Actions")
    st.caption("Click any prompt to ask the AI assistant:")

    quick_prompts = [
        "Read my latest 3 emails and summarize key info.",
        "Check my Google Calendar for today.",
        "Check my schedule for tomorrow and list free slots.",
        "Create a calendar event for Team Standup tomorrow at 10 AM.",
    ]

    for qp in quick_prompts:
        if st.button(qp, use_container_width=True):
            st.session_state["pending_prompt"] = qp

    st.markdown("---")
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state["messages"] = []
        st.rerun()

# Main Application Layout
st.markdown("""
<div class="main-header">
    <div>
        <h1 class="main-title">🧠 Smart Scheduler Assistant</h1>
        <p class="subtitle">AI-powered Gmail reader & Google Calendar automated scheduling assistant</p>
    </div>
    <div>
        <span class="badge badge-success">● Active</span>
        <span class="badge badge-info">Multi-Agent System</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Application Tabs
tab_chat, tab_calendar, tab_emails = st.tabs(["💬 AI Assistant", "📅 Calendar Explorer", "📧 Inbox Explorer"])

# Initialize session state for chat messages
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "Hello! 👋 I am your Smart Scheduler Assistant. I can read your Gmail messages, summarize important updates, check your Google Calendar, and schedule events for you. How can I assist you today?"}
    ]

# TAB 1: Chat Assistant
with tab_chat:
    # Render chat history
    for msg in st.session_state["messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Check for quick prompt selection from sidebar
    prompt_input = st.chat_input("Type your request (e.g. 'Read latest emails' or 'Schedule meeting tomorrow at 3 PM')...")
    
    if "pending_prompt" in st.session_state and st.session_state["pending_prompt"]:
        prompt_input = st.session_state["pending_prompt"]
        st.session_state["pending_prompt"] = None

    if prompt_input:
        # User message
        st.session_state["messages"].append({"role": "user", "content": prompt_input})
        with st.chat_message("user"):
            st.markdown(prompt_input)

        # Assistant response
        with st.chat_message("assistant"):
            if team is None:
                st.error("Assistant engine is not configured properly. Check system status in the sidebar.")
            else:
                with st.spinner("🤖 Processing request with Gmail & Calendar agents..."):
                    try:
                        run_response = team.run(prompt_input)
                        response_text = run_response.content if hasattr(run_response, 'content') else str(run_response)
                        st.markdown(response_text)
                        st.session_state["messages"].append({"role": "assistant", "content": response_text})
                    except Exception as e:
                        error_msg = f"❌ Error executing request: {e}"
                        st.error(error_msg)
                        st.session_state["messages"].append({"role": "assistant", "content": error_msg})

# TAB 2: Calendar Explorer
with tab_calendar:
    st.markdown("### 📅 Live Google Calendar Scanner")
    st.write("Scan your upcoming schedule directly with one click.")
    
    col_cal_1, col_cal_2 = st.columns([1, 4])
    with col_cal_1:
        fetch_cal = st.button("🔄 Fetch Today's Events", key="btn_fetch_cal", use_container_width=True)
    
    if fetch_cal:
        if team:
            with st.spinner("Fetching Google Calendar events..."):
                try:
                    cal_res = team.run("List all scheduled calendar events for today with start time, end time, and event title.")
                    st.markdown(cal_res.content if hasattr(cal_res, 'content') else str(cal_res))
                except Exception as e:
                    st.error(f"Failed to fetch calendar: {e}")
        else:
            st.warning("Please check system authentication in sidebar.")

# TAB 3: Inbox Explorer
with tab_emails:
    st.markdown("### 📧 Live Gmail Scanner")
    st.write("Fetch recent emails and identify potential scheduling requests.")
    
    col_em_1, col_em_2 = st.columns([1, 4])
    with col_em_1:
        fetch_em = st.button("🔄 Fetch Latest Emails", key="btn_fetch_emails", use_container_width=True)
        
    if fetch_em:
        if team:
            with st.spinner("Reading latest 5 Gmail messages..."):
                try:
                    em_res = team.run("Search and read the latest 5 emails in Gmail. Display sender, date/time, subject, and a brief summary.")
                    st.markdown(em_res.content if hasattr(em_res, 'content') else str(em_res))
                except Exception as e:
                    st.error(f"Failed to read emails: {e}")
        else:
            st.warning("Please check system authentication in sidebar.")
