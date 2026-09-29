from agno.agent import Agent
from typing import Iterator
from agno.team import Team, TeamRunOutputEvent
from agno.tools.google.gmail import GmailTools
from agno.tools.google.sheets import GoogleSheetsTools
from agno.tools.google.calendar import GoogleCalendarTools
import dotenv
from dotenv import load_dotenv
from agno.utils.pprint import pprint_run_response
from agno.db.sqlite import SqliteDb
import os
import sys

load_dotenv()
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

timezone = os.getenv("TIMEZONE", "Asia/Kolkata")

# LLM Provider Detection
groq_api_key = os.getenv("GROQ_API_KEY")
gemini_api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")
nebius_api_key = os.getenv("NEBIUS_API_KEY")

if groq_api_key:
    from agno.models.groq import Groq
    model = Groq(id="llama-3.3-70b-versatile", api_key=groq_api_key)
    print("🤖 LLM Provider: Groq (llama-3.3-70b-versatile)")
elif gemini_api_key:
    from agno.models.google import Gemini
    model = Gemini(id="gemini-2.5-flash", api_key=gemini_api_key)
    print("🤖 LLM Provider: Google Gemini (gemini-2.5-flash)")
elif openai_api_key:
    from agno.models.openai import OpenAIChat
    model = OpenAIChat(id="gpt-4o-mini", api_key=openai_api_key)
    print("🤖 LLM Provider: OpenAI (gpt-4o-mini)")
elif nebius_api_key:
    from agno.models.nebius import Nebius
    model = Nebius(id="Qwen/Qwen3-32b", api_key=nebius_api_key)
    print("🤖 LLM Provider: Nebius (Qwen3-32b)")
else:
    print("❌ Error: No LLM API key found in environment.")
    print("Please set one of the following in your .env file:")
    print("  - GROQ_API_KEY (Free at https://console.groq.com)")
    print("  - GEMINI_API_KEY (Free at https://aistudio.google.com)")
    print("  - OPENAI_API_KEY (https://platform.openai.com)")
    print("  - NEBIUS_API_KEY (https://studio.nebius.ai)")
    sys.exit(1)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CREDS_PATH = os.path.join(SCRIPT_DIR, "credentials.json")
TOKEN_PATH = os.path.join(SCRIPT_DIR, "token.json")
DB_PATH = os.getenv("DB_PATH", os.path.join(SCRIPT_DIR, "tmp", "data.db"))
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# Validate required files
if not os.path.exists(CREDS_PATH):
    print("❌ Error: credentials.json not found.")
    print("Please download OAuth credentials from Google Cloud Console.")
    sys.exit(1)

if not os.path.exists(TOKEN_PATH):
    print("❌ Error: token.json not found.")
    print("Please run 'python authenticate.py' first to generate token.json.")
    sys.exit(1)

db = SqliteDb(db_file=DB_PATH)

email_agent = Agent(
    model=model,
    markdown=True,
    tools=[GmailTools(credentials_path=CREDS_PATH, token_path=TOKEN_PATH)],
    description="You are a Gmail reading specialist that can search and read emails.",
    instructions=[
        "Use the tools to search and read emails from Gmail.",
        "Limit email searches/fetches to a maximum of 3-5 latest emails to remain fast and token-efficient.",
        "Focus on extracting key details such as sender, subject, and concise summary of the body.",
        "Never fabricate email content; only use the information available in the emails.",
        "If no emails are found, respond with 'No emails found.'",
    ],
    db=db,
    add_history_to_context=True,
    num_history_runs=3,
    read_chat_history=True,
)

calendar_agent = Agent(
    model=model,
    description="You are a Google Calendar specialist that can create, view, update, and delete calendar events.",
    tools=[
        GoogleCalendarTools(
            credentials_path=CREDS_PATH,
            token_path=TOKEN_PATH,
        )
    ],
    instructions=[
        f"""
    You are a scheduling assistant.
    You should help users to perform these actions in their Google calendar:
        - get their scheduled events from a certain date and time
        - create events based on provided details
        - update existing events
        - delete events
        - find available time slots for scheduling
        - all times are in {timezone}
    """
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
    description="Team to manage Gmail emails and Google Calendar events.",
    model=model,
    instructions=[
        "Analyze the user's request:",
        "- If the request is directly about Google Calendar (e.g. creating, listing, updating, or deleting events), delegate directly to the calendar_agent.",
        "- If the request is about reading emails or converting email information into calendar events, first use the email_agent to search/read emails, then use the calendar_agent to update Google Calendar accordingly.",
        "Ensure all necessary event details (name, date, time) are provided when managing calendar events.",
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
            print("⚠️  Please enter a message.\n")
            user_input = input("You: ")
            continue

        try:
            run_response = team.run(user_input)
            print("\nAgent:", run_response.content, "\n")
        except Exception as e:
            print(f"❌ Error: {e}\n")

        user_input = input("You: ")
