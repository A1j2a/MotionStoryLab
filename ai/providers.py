import os
import re
import json
import logging
import urllib.request
import urllib.error
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod
from ai.json_utils import extract_and_repair_json

logger = logging.getLogger("studio.ai.providers")


def _get_db_config(key: str) -> str:
    try:
        import sqlite3
        from pathlib import Path
        db_path = Path(__file__).resolve().parent.parent / "projects" / "studio.db"
        if db_path.exists():
            conn = sqlite3.connect(str(db_path), timeout=5)
            c = conn.cursor()
            c.execute("SELECT value FROM studio_config WHERE key = ?", (key,))
            row = c.fetchone()
            conn.close()
            if row and row[0]:
                return row[0].strip()
    except Exception:
        pass
    return ""


class BaseAIProvider(ABC):
    """Abstract base class for all AI text/reasoning providers."""

    @abstractmethod
    def generate_json(self, prompt: str, system_prompt: str = "", max_tokens: Optional[int] = None) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def generate_text(self, prompt: str, system_prompt: str = "", max_tokens: Optional[int] = None) -> Optional[str]:
        pass


class OpenRouterProvider(BaseAIProvider):
    """
    OpenRouter Universal LLM Gateway (DeepSeek R1, Claude 3.5, Gemini 2.0, Llama 3.3).
    Supports 592+ models and robust JSON extraction.
    """

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None, base_url: Optional[str] = None):
        db_key = _get_db_config("OPENROUTER_API_KEY")
        db_model = _get_db_config("OPENROUTER_MODEL")
        self.api_key = (api_key or db_key or os.environ.get("OPENROUTER_API_KEY", "")).strip()
        self.model = (model or db_model or os.environ.get("OPENROUTER_MODEL", "meta-llama/llama-3.3-70b-instruct")).strip()
        self.base_url = (base_url or os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")).rstrip("/")
        self.last_error = ""

    def _call_api(self, prompt: str, system_prompt: str = "", temperature: float = 0.7, max_tokens: Optional[int] = None) -> Optional[str]:
        if not self.api_key:
            self.last_error = "OpenRouter API Key not set. Please add it in Settings."
            logger.warning("OpenRouter API Key not set.")
            return None

        target_url = f"{self.base_url}/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "http://127.0.0.1:3000",
            "X-Title": "MotionStoryLab AI Studio",
        }

        token_limit = min(max_tokens or 2500, 3500)

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt or "You are an elite preschool animation, viral nursery rhyme, and YouTube Kids creator. Output strictly valid JSON only.",
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": temperature,
            "max_tokens": token_limit,
        }

        try:
            req = urllib.request.Request(
                target_url,
                data=json.dumps(payload).encode("utf-8"),
                headers=headers,
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=60) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode("utf-8"))
                    choices = data.get("choices", [])
                    if choices and "message" in choices[0]:
                        return choices[0]["message"].get("content", "")
        except urllib.error.HTTPError as e:
            err_text = ""
            try:
                err_body = json.loads(e.read().decode("utf-8"))
                err_text = err_body.get("error", {}).get("message", str(e))
            except Exception:
                err_text = str(e)
            self.last_error = f"HTTP {e.code}: {err_text}"
            logger.warning(f"OpenRouter API call failed to {target_url} (Model: {self.model}): {self.last_error}")
            return None
        except Exception as e:
            self.last_error = str(e)
            logger.warning(f"OpenRouter API call failed to {target_url} (Model: {self.model}): {e}")
            return None
        return None

    def generate_json(self, prompt: str, system_prompt: str = "", max_tokens: Optional[int] = None) -> Optional[Dict[str, Any]]:
        raw = self._call_api(prompt, system_prompt, max_tokens=max_tokens)
        if not raw:
            return None
        parsed = extract_and_repair_json(raw)
        if parsed is None:
            self.last_error = f"LLM response could not be parsed into JSON (length: {len(raw)})"
        return parsed

    def generate_text(self, prompt: str, system_prompt: str = "", max_tokens: Optional[int] = None) -> Optional[str]:
        raw = self._call_api(prompt, system_prompt, max_tokens=max_tokens)
        if not raw:
            return None
        return re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL).strip()


class OmniRouteProvider(BaseAIProvider):
    """
    OmniRoute AI Gateway (Local OpenAI-compatible endpoint).
    Default: http://127.0.0.1:20128
    """

    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None, model: Optional[str] = None):
        self.base_url = (base_url or os.environ.get("OMNIROUTE_URL", "http://127.0.0.1:20128")).rstrip("/")
        self.api_key = api_key or os.environ.get("OMNIROUTE_API_KEY", "")
        self.model = model or os.environ.get("OMNIROUTE_MODEL", "omniroute-default")

    def _call_api(self, prompt: str, system_prompt: str = "", temperature: float = 0.7) -> Optional[str]:
        target_url = f"{self.base_url}/v1/chat/completions"
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt or "You are an expert AI Kids Video Creator. Output valid JSON only."},
                {"role": "user", "content": prompt},
            ],
            "temperature": temperature,
            "max_tokens": 3000,
        }

        try:
            req = urllib.request.Request(
                target_url,
                data=json.dumps(payload).encode("utf-8"),
                headers=headers,
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=60) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode("utf-8"))
                    return data["choices"][0]["message"]["content"]
        except Exception as e:
            logger.warning(f"OmniRoute call to {target_url} failed: {e}")
            return None
        return None

    def generate_json(self, prompt: str, system_prompt: str = "", max_tokens: Optional[int] = None) -> Optional[Dict[str, Any]]:
        raw = self._call_api(prompt, system_prompt)
        if not raw:
            return None
        return extract_and_repair_json(raw)

    def generate_text(self, prompt: str, system_prompt: str = "", max_tokens: Optional[int] = None) -> Optional[str]:
        return self._call_api(prompt, system_prompt)


class OllamaProvider(BaseAIProvider):
    """
    Ollama Local AI Provider (Apple Silicon Metal GPU).
    Default: http://127.0.0.1:11434
    """

    def __init__(self, base_url: Optional[str] = None, model: Optional[str] = None):
        self.base_url = (base_url or os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434")).rstrip("/")
        self.model = model or os.environ.get("OLLAMA_MODEL", "llama3.2")

    def _call_api(self, prompt: str, system_prompt: str = "", temperature: float = 0.7) -> Optional[str]:
        target_url = f"{self.base_url}/v1/chat/completions"
        headers = {"Content-Type": "application/json"}

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt or "You are an expert preschool animation & music creator. Return valid JSON only."},
                {"role": "user", "content": prompt},
            ],
            "temperature": temperature,
            "max_tokens": 2500,
        }

        try:
            req = urllib.request.Request(
                target_url,
                data=json.dumps(payload).encode("utf-8"),
                headers=headers,
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=60) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode("utf-8"))
                    return data["choices"][0]["message"]["content"]
        except Exception as e:
            logger.warning(f"Ollama call to {target_url} failed: {e}")
            return None
        return None

    def generate_json(self, prompt: str, system_prompt: str = "", max_tokens: Optional[int] = None) -> Optional[Dict[str, Any]]:
        raw = self._call_api(prompt, system_prompt)
        if not raw:
            return None
        return extract_and_repair_json(raw)

    def generate_text(self, prompt: str, system_prompt: str = "", max_tokens: Optional[int] = None) -> Optional[str]:
        return self._call_api(prompt, system_prompt)


class ClaudeProvider(BaseAIProvider):
    """
    Anthropic Claude 3.5 Sonnet Provider.
    """

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY", os.environ.get("CLAUDE_API_KEY", "")).strip()
        self.model = model or os.environ.get("CLAUDE_MODEL", "claude-3-5-sonnet-20241022").strip()

    def _call_api(self, prompt: str, system_prompt: str = "") -> Optional[str]:
        if not self.api_key:
            return None

        target_url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }

        payload = {
            "model": self.model,
            "max_tokens": 3000,
            "system": system_prompt or "You are an elite preschool animation and YouTube Kids creator. Output valid JSON only.",
            "messages": [{"role": "user", "content": prompt}],
        }

        try:
            req = urllib.request.Request(
                target_url,
                data=json.dumps(payload).encode("utf-8"),
                headers=headers,
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=60) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode("utf-8"))
                    for block in data.get("content", []):
                        if block.get("type") == "text":
                            return block.get("text", "")
        except Exception as e:
            logger.warning(f"Claude API call failed: {e}")
            return None
        return None

    def generate_json(self, prompt: str, system_prompt: str = "", max_tokens: Optional[int] = None) -> Optional[Dict[str, Any]]:
        raw = self._call_api(prompt, system_prompt)
        if not raw:
            return None
        return extract_and_repair_json(raw)

    def generate_text(self, prompt: str, system_prompt: str = "", max_tokens: Optional[int] = None) -> Optional[str]:
        return self._call_api(prompt, system_prompt)


class FallbackAIProvider(BaseAIProvider):
    """
    Fallback engine.
    """

    def generate_json(self, prompt: str, system_prompt: str = "", max_tokens: Optional[int] = None) -> Optional[Dict[str, Any]]:
        return None

    def generate_text(self, prompt: str, system_prompt: str = "", max_tokens: Optional[int] = None) -> Optional[str]:
        return "Preschool AI Fallback Generated Text"


def get_ai_provider() -> BaseAIProvider:
    """
    Factory function: Returns configured AI provider.
    Checks SQLite studio_config first, then environment variables.
    OpenRouter (if enabled) -> Claude -> OmniRoute -> Ollama -> Fallback.
    """
    db_enabled = _get_db_config("OPENROUTER_ENABLED")
    db_key = _get_db_config("OPENROUTER_API_KEY")
    db_model = _get_db_config("OPENROUTER_MODEL")

    openrouter_enabled = (db_enabled.lower() in ("true", "1", "yes")) if db_enabled else (os.environ.get("OPENROUTER_ENABLED", "false").strip().lower() in ("true", "1", "yes"))
    openrouter_key = db_key or os.environ.get("OPENROUTER_API_KEY", "").strip()
    openrouter_model = db_model or os.environ.get("OPENROUTER_MODEL", "meta-llama/llama-3.3-70b-instruct").strip()
    preferred = os.environ.get("AI_PROVIDER", "").strip().lower()

    if (openrouter_enabled or preferred == "openrouter") and openrouter_key:
        return OpenRouterProvider(api_key=openrouter_key, model=openrouter_model)

    if preferred == "omniroute":
        return OmniRouteProvider()
    elif preferred == "claude" and os.environ.get("ANTHROPIC_API_KEY"):
        return ClaudeProvider()
    elif preferred == "ollama":
        return OllamaProvider()

    # Cascade automatically
    if os.environ.get("ANTHROPIC_API_KEY"):
        return ClaudeProvider()

    # Test OmniRoute if URL is explicitly set, else Ollama
    if os.environ.get("OMNIROUTE_URL"):
        return OmniRouteProvider()

    return OllamaProvider()
