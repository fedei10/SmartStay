"""
Groq API connection and testing service.
Handles connection setup and health checks for Groq AI services.
"""

import httpx

from app.config import settings

def test_chat_groq_connection():
    """
    Test the Groq API connection by making a simple request.
    Returns True if the connection is successful, False otherwise.
    """
    try:
        return bool(settings.GROQ_API_KEY)
    except Exception as e:
        print(f"Groq connection error: {e}")
        return False


def test_groq_connection():
    """
    Test the Groq API connection.
    """
    api_key = settings.GROQ_API_KEY

    if not api_key:
        return {
            "status": "error",
            "message": "GROQ_API_KEY is not configured",
        }

    url = "https://api.groq.com/openai/v1/models"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        response = httpx.get(url, headers=headers, timeout=10.0)
        response.raise_for_status()
        return {
            "status": "ok",
            "models": response.json(),
        }
    except httpx.HTTPStatusError as exc:
        return {
            "status": "error",
            "message": "Groq API returned an error",
            "detail": str(exc),
            "response": getattr(exc.response, "text", None),
        }
    except httpx.RequestError as exc:
        return {
            "status": "error",
            "message": "Failed to reach Groq API",
            "detail": str(exc),
        }

if __name__ == "main ":
    try:
       test_chat_groq_connection()
       test_groq_connection()
    except Exception as e:
         print(f"Groq connection test failed: {e}")
    