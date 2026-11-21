"""
Configuration Loader for SkillLens.
Loads environment variables from .env file without external dependencies.
"""
import os
from pathlib import Path

# Load .env file manually if it exists
env_path = Path(__file__).resolve().parent.parent / '.env'
if env_path.exists():
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, val = line.split('=', 1)
                os.environ.setdefault(key.strip(), val.strip())

# Application Settings
FLASK_SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'skilllens-hackathon-secret-key-2026')
FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() in ('true', '1', 't')

# Supabase Credentials
SUPABASE_URL = os.getenv('SUPABASE_URL', '').rstrip('/')
SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY', '')

# Gemini AI Key
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')

def is_supabase_configured() -> bool:
    return bool(SUPABASE_URL and SUPABASE_ANON_KEY)

def is_gemini_configured() -> bool:
    return bool(GEMINI_API_KEY)
