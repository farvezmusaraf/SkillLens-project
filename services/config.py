"""
Configuration Loader for SkillLens.
Loads environment variables from .env file using python-dotenv.
Supports both SUPABASE_PUBLISHABLE_KEY and SUPABASE_ANON_KEY seamlessly.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Path to .env file in the project root
BASE_DIR = Path(__file__).resolve().parent.parent
env_path = BASE_DIR / '.env'

if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()

# Application Settings
FLASK_SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'skilllens-hackathon-secret-key-2026')
FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() in ('true', '1', 't')

# Supabase Credentials
# Supports both SUPABASE_PUBLISHABLE_KEY and legacy SUPABASE_ANON_KEY
SUPABASE_URL = os.getenv('SUPABASE_URL', '').strip().rstrip('/')
SUPABASE_PUBLISHABLE_KEY = (os.getenv('SUPABASE_PUBLISHABLE_KEY') or os.getenv('SUPABASE_ANON_KEY') or '').strip()
SUPABASE_ANON_KEY = SUPABASE_PUBLISHABLE_KEY  # Backward compatibility alias

# Gemini AI Key
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '').strip()

def is_supabase_configured() -> bool:
    """Returns True if valid Supabase URL and Key are provided."""
    return bool(SUPABASE_URL and SUPABASE_PUBLISHABLE_KEY)

def is_gemini_configured() -> bool:
    return bool(GEMINI_API_KEY)
