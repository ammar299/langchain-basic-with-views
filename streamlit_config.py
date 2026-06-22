import os
from pathlib import Path

try:
    import streamlit as st
except ImportError:
    st = None

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None


def init_google_api_key() -> None:
    """Initialize GOOGLE_API_KEY from environment, Streamlit secrets, or local .env.

    Priority:
    1. Existing environment variable
    2. Streamlit secrets (deployment)
    3. Local .env file (development)
    """
    if os.environ.get("GOOGLE_API_KEY"):
        return

    if st is not None:
        try:
            secret_key = st.secrets.get("GOOGLE_API_KEY")
        except Exception:
            secret_key = None
        if secret_key:
            os.environ["GOOGLE_API_KEY"] = secret_key
            return

    if load_dotenv is not None:
        env_path = Path(".env")
        if env_path.exists():
            load_dotenv(dotenv_path=env_path, override=False)
            env_key = os.environ.get("GOOGLE_API_KEY")
            if env_key:
                return
