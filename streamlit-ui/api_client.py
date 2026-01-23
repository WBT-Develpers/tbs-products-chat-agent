from typing import Any, Dict, Optional, Tuple

import requests

from config import PINECONE_API_URL, SUPABASE_API_URL


class APIError(Exception):
    """Base exception for API errors."""
    def __init__(self, message: str, status_code: Optional[int] = None, details: Optional[str] = None):
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(self.message)


class NetworkError(APIError):
    """Network-related errors (connection, timeout, etc.)."""
    pass


class APIRequestError(APIError):
    """API request errors (4xx, 5xx)."""
    pass


class BaseAPIClient:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")

    def _parse_error(self, response: requests.Response) -> Tuple[str, str]:
        """Parse error response and return user-friendly message and details."""
        try:
            error_data = response.json()
            detail = error_data.get("detail", error_data.get("message", "Unknown error"))
            return f"API Error ({response.status_code})", str(detail)
        except Exception:
            return f"API Error ({response.status_code})", response.text[:200] or "No error details available"

    def _handle_request(self, method: str, url: str, **kwargs) -> requests.Response:
        """Handle HTTP request with better error handling."""
        try:
            resp = requests.request(method, url, **kwargs)
            return resp
        except requests.exceptions.Timeout:
            raise NetworkError("Request timed out. The server may be slow or unavailable. Please try again.")
        except requests.exceptions.ConnectionError:
            raise NetworkError("Could not connect to the API. Please check your internet connection and API URL.")
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"Network error: {str(e)}")

    def chat(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}/api/chat"
        resp = self._handle_request("POST", url, json=payload, timeout=60)
        if resp.status_code != 200:
            msg, details = self._parse_error(resp)
            raise APIRequestError(msg, resp.status_code, details)
        return resp.json()

    def reset_session(self, session_id: str) -> Dict[str, Any]:
        url = f"{self.base_url}/api/reset"
        resp = self._handle_request("POST", url, json={"session_id": session_id}, timeout=30)
        if resp.status_code != 200:
            msg, details = self._parse_error(resp)
            raise APIRequestError(msg, resp.status_code, details)
        return resp.json()

    def health_check(self) -> Tuple[bool, Optional[str]]:
        """Check API health. Returns (is_healthy, error_message)."""
        try:
            url = f"{self.base_url}/health"
            resp = self._handle_request("GET", url, timeout=10)
            if resp.status_code == 200:
                return True, None
            else:
                return False, f"Health check returned status {resp.status_code}"
        except Exception as e:
            return False, str(e)


class PineconeAPIClient(BaseAPIClient):
    def __init__(self) -> None:
        super().__init__(PINECONE_API_URL)

    def build_payload(
        self,
        message: str,
        session_id: Optional[str],
        temperature: Optional[float],
        chat_model: Optional[str],
        k: Optional[int],
        filters: Optional[Dict[str, Any]],
        system_prompt: Optional[str],
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {"message": message}
        if session_id:
            payload["session_id"] = session_id
        if temperature is not None:
            payload["temperature"] = temperature
        if chat_model:
            payload["chat_model"] = chat_model
        if k is not None:
            payload["k"] = k
        if filters:
            payload["filters"] = filters
        if system_prompt:
            payload["system_prompt"] = system_prompt
        return payload


class SupabaseAPIClient(BaseAPIClient):
    def __init__(self) -> None:
        super().__init__(SUPABASE_API_URL)

    def build_payload(
        self,
        message: str,
        session_id: Optional[str],
        temperature: Optional[float],
        chat_model: Optional[str],
        embedding_model: Optional[str],
        k: Optional[int],
        filters: Optional[Dict[str, Any]],
        system_prompt: Optional[str],
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {"message": message}
        if session_id:
            payload["session_id"] = session_id
        if temperature is not None:
            payload["temperature"] = temperature
        if chat_model:
            payload["chat_model"] = chat_model
        if embedding_model:
            payload["embedding_model"] = embedding_model
        if k is not None:
            payload["k"] = k
        if filters:
            payload["filters"] = filters
        if system_prompt:
            payload["system_prompt"] = system_prompt
        return payload

