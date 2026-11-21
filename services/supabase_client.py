"""
Supabase Client Initializer for SkillLens.
Initializes the official Supabase Python client using create_client.
Handles missing environment variables and connection errors gracefully.
"""
import logging
from typing import Optional, Tuple
from supabase import create_client, Client
from .config import SUPABASE_URL, SUPABASE_PUBLISHABLE_KEY, is_supabase_configured

logger = logging.getLogger(__name__)

# Singleton client instance
_supabase_client: Optional[Client] = None

def get_supabase_client() -> Optional[Client]:
    """
    Returns the initialized Supabase client singleton, or None if unconfigured.
    Never exposes credentials or crashes the application if environment variables are missing.
    """
    global _supabase_client
    if _supabase_client is not None:
        return _supabase_client

    if not is_supabase_configured():
        return None

    try:
        _supabase_client = create_client(SUPABASE_URL, SUPABASE_PUBLISHABLE_KEY)
        return _supabase_client
    except Exception as e:
        logger.warning("Could not initialize Supabase client: %s", type(e).__name__)
        return None

def check_supabase_connection() -> Tuple[bool, str]:
    """
    Safely tests the Supabase connection by reading from the skills catalog table.
    Returns (status: bool, message: str).
    Never exposes secret credentials in logs or output.
    """
    if not is_supabase_configured():
        return False, "Supabase credentials are not configured in .env. Running in Local SQLite Demo mode."

    client = get_supabase_client()
    if not client:
        return False, "Failed to initialize Supabase client with the provided credentials."

    try:
        # Perform a safe read operation on the skills catalog (limit 1)
        response = client.table("skills").select("name").limit(1).execute()
        return True, "Successfully connected to Supabase Cloud PostgreSQL database."
    except Exception as e:
        err_msg = str(e).lower()
        if "relation" in err_msg and "does not exist" in err_msg:
            return False, "Connected to Supabase, but tables are missing. Please execute database/schema.sql in the Supabase SQL Editor."
        return False, f"Supabase connection check: {type(e).__name__}"
