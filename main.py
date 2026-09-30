import os
import sys
from agno.agent import Agent
from agno.team import Team
from agno.tools.google.gmail import GmailTools
from agno.tools.google.calendar import GoogleCalendarTools
from agno.db.sqlite import SqliteDb
from agno.utils.pprint import pprint_run_response
from dotenv import load_dotenv

load_dotenv()
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

timezone = os.getenv("TIMEZONE", "Asia/Kolkata")

# LLM Provider — picks the first available API key
groq_api_key = os.getenv("GROQ_API_KEY")
gemini_api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")

if groq_api_key:
    from agno.models.groq import Groq
    model = Groq(id="llama-3.3-70b-versatile", api_key=groq_api_key)
    print("🤖 LLM Provider: Groq (llama-3.3-70b-versatile)")
elif gemini_api_key:
    from agno.models.google import Gemini
    model_id = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    model = Gemini(id=model_id, api_key=gemini_api_key)
    print(f"🤖 LLM Provider: Google Gemini ({model_id})")
elif openai_api_key:
    from agno.models.openai import OpenAIChat
    model = OpenAIChat(id="gpt-4o-mini", api_key=openai_api_key)
    print("🤖 LLM Provider: OpenAI (gpt-4o-mini)")
else:
    print("❌ No LLM API key found. Set GEMINI_API_KEY, GROQ_API_KEY, or OPENAI_API_KEY in .env")
    sys.exit(1)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CREDS_PATH = os.path.join(SCRIPT_DIR, "credentials.json")
TOKEN_PATH = os.path.join(SCRIPT_DIR, "token.json")
DB_PATH = os.getenv("DB_PATH", os.path.join(SCRIPT_DIR, "tmp", "data.db"))
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

if not os.path.exists(CREDS_PATH):
    print("❌ credentials.json not found. Download it from Google Cloud Console.")
    sys.exit(1)

if not os.path.exists(TOKEN_PATH):
    print("❌ token.json not found. Run 'python authenticate.py' first.")
    sys.exit(1)

db = SqliteDb(db_file=DB_PATH)

email_agent = Agent(
    model=model,
    markdown=True,
    tools=[GmailTools(credentials_path=CREDS_PATH, token_path=TOKEN_PATH)],
    description="Gmail reading specialist.",
    instructions=[
        "Use tools to search and read emails from Gmail.",
        "Limit fetches to the 5 latest emails.",
        "Extract sender, subject, and a concise body summary.",
        "Never fabricate email content.",
        "If no emails are found, respond with 'No emails found.'",
    ],
    db=db,
    add_history_to_context=True,
    num_history_runs=3,
    read_chat_history=True,
)

calendar_agent = Agent(
    model=model,
    description="Google Calendar specialist.",
    tools=[GoogleCalendarTools(credentials_path=CREDS_PATH, token_path=TOKEN_PATH)],
    instructions=[
        f"""You are a scheduling assistant. Help users:
        - View scheduled events for a given date/time
        - Create new calendar events
        - Update or delete existing events
        - Find available time slots
        - All times are in {timezone}"""
    ],
    add_datetime_to_context=True,
    db=db,
    add_history_to_context=True,
    num_history_runs=3,
    read_chat_history=True,
)

team = Team(
    name="Productivity Agent",
    members=[email_agent, calendar_agent],
    description="Manages Gmail emails and Google Calendar events.",
    model=model,
    instructions=[
        "Analyze the user's request:",
        "- Calendar requests → delegate to calendar_agent.",
        "- Email-to-event requests → use email_agent, then calendar_agent.",
        "Ensure event details (name, date, time) are complete before creating events.",
    ],
    db=db,
    add_history_to_context=True,
    num_history_runs=3,
    read_chat_history=True,
)

if __name__ == "__main__":
    print("\n🧠 Smart Scheduler Assistant is running. Type 'exit' to quit.\n")
    user_input = input("You: ")

    while True:
        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye 👋")
            break

        if not user_input.strip():
            user_input = input("You: ")
            continue

        try:
            run_response = team.run(user_input)
            print("\nAgent:", run_response.content, "\n")
        except Exception as e:
            print(f"❌ Error: {e}\n")

        user_input = input("You: ")
