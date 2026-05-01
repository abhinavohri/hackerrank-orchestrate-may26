import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
HACKERRANK_DIR = DATA_DIR / "hackerrank"
CLAUDE_DIR = DATA_DIR / "claude"
VISA_DIR = DATA_DIR / "visa"

INPUT_CSV = PROJECT_ROOT / "support_tickets" / "support_tickets.csv"
SAMPLE_CSV = PROJECT_ROOT / "support_tickets" / "sample_support_tickets.csv"
OUTPUT_CSV = PROJECT_ROOT / "support_tickets" / "output.csv"

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
SUPABASE_DB_URL = os.environ.get("SUPABASE_DB_URL", "")

EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "gemini-embedding-2")
LLM_MODEL = os.environ.get("LLM_MODEL", "gemini-2.5-flash")
LLM_TEMPERATURE = 0
SEED = 42

EMBEDDING_DIMENSION = 768
TOP_K_RETRIEVAL = 10
TOP_K_FINAL = 5

DOMAIN_MAP = {
    "hackerrank": "hackerrank",
    "claude": "claude",
    "visa": "visa",
}

PRODUCT_AREA_MAP = {
    "hackerrank/screen": "screen",
    "hackerrank/interviews": "interviews",
    "hackerrank/library": "library",
    "hackerrank/engage": "engage",
    "hackerrank/chakra": "chakra",
    "hackerrank/skillup": "skillup",
    "hackerrank/integrations": "integrations",
    "hackerrank/settings": "settings",
    "hackerrank/general-help": "general_help",
    "hackerrank/hackerrank_community": "community",
    "hackerrank/uncategorized": "general_help",
    "claude/claude/account-management": "account_management",
    "claude/claude/conversation-management": "conversation_management",
    "claude/claude/features-and-capabilities": "features_and_capabilities",
    "claude/privacy-and-legal": "privacy",
    "claude/safeguards": "safeguards",
    "claude/team-and-enterprise-plans": "team_and_enterprise",
    "claude/pro-and-max-plans": "pro_and_max_plans",
    "claude/claude-code": "claude_code",
    "claude/claude-for-education": "claude_for_education",
    "claude/amazon-bedrock": "amazon_bedrock",
    "claude/connectors": "connectors",
    "claude/claude-desktop": "claude_desktop",
    "claude/claude-mobile-apps": "claude_mobile",
    "claude/identity-management-sso-jit-scim": "identity_management",
    "claude/claude-for-government": "claude_for_government",
    "claude/claude-for-nonprofits": "claude_for_nonprofits",
    "claude/claude-in-chrome": "claude_in_chrome",
    "claude/claude-api-and-console": "claude_api",
    "visa/support/consumer/travel-support": "travel_support",
    "visa/support/consumer": "general_support",
    "visa/support/small-business": "small_business",
}
