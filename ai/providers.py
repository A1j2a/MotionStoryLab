import os
import re
import json
import logging
import urllib.request
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod

logger = logging.getLogger("studio.ai.providers")


class BaseAIProvider(ABC):
    """Abstract base class for all AI text/reasoning providers."""

    @abstractmethod
    def generate_json(self, prompt: str, system_prompt: str = "") -> Optional[Dict[str, Any]]:
        """Generates structured JSON from the model."""
        pass

    @abstractmethod
    def generate_text(self, prompt: str, system_prompt: str = "") -> Optional[str]:
        """Generates raw text response."""
        pass


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
            with urllib.request.urlopen(req, timeout=15) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode("utf-8"))
                    return data["choices"][0]["message"]["content"]
        except Exception as e:
            logger.warning(f"OmniRoute call to {target_url} failed: {e}")
            return None
        return None

    def generate_json(self, prompt: str, system_prompt: str = "") -> Optional[Dict[str, Any]]:
        raw = self._call_api(prompt, system_prompt)
        if not raw:
            return None
        clean = re.sub(r"^```(?:json)?\s*", "", raw.strip(), flags=re.MULTILINE)
        clean = re.sub(r"```$", "", clean.strip(), flags=re.MULTILINE)
        try:
            return json.loads(clean)
        except Exception as e:
            logger.warning(f"Failed to parse OmniRoute JSON: {e} | Raw: {raw[:150]}")
            return None

    def generate_text(self, prompt: str, system_prompt: str = "") -> Optional[str]:
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
            with urllib.request.urlopen(req, timeout=12) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode("utf-8"))
                    return data["choices"][0]["message"]["content"]
        except Exception as e:
            logger.warning(f"Ollama call to {target_url} failed: {e}")
            return None
        return None

    def generate_json(self, prompt: str, system_prompt: str = "") -> Optional[Dict[str, Any]]:
        raw = self._call_api(prompt, system_prompt)
        if not raw:
            return None
        clean = re.sub(r"^```(?:json)?\s*", "", raw.strip(), flags=re.MULTILINE)
        clean = re.sub(r"```$", "", clean.strip(), flags=re.MULTILINE)
        try:
            return json.loads(clean)
        except Exception as e:
            logger.warning(f"Failed to parse Ollama JSON: {e} | Raw: {raw[:150]}")
            return None

    def generate_text(self, prompt: str, system_prompt: str = "") -> Optional[str]:
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
            with urllib.request.urlopen(req, timeout=15) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode("utf-8"))
                    for block in data.get("content", []):
                        if block.get("type") == "text":
                            return block.get("text", "")
        except Exception as e:
            logger.warning(f"Claude API call failed: {e}")
            return None
        return None

    def generate_json(self, prompt: str, system_prompt: str = "") -> Optional[Dict[str, Any]]:
        raw = self._call_api(prompt, system_prompt)
        if not raw:
            return None
        clean = re.sub(r"^```(?:json)?\s*", "", raw.strip(), flags=re.MULTILINE)
        clean = re.sub(r"```$", "", clean.strip(), flags=re.MULTILINE)
        try:
            return json.loads(clean)
        except Exception as e:
            logger.warning(f"Failed to parse Claude JSON: {e} | Raw: {raw[:150]}")
            return None

    def generate_text(self, prompt: str, system_prompt: str = "") -> Optional[str]:
        return self._call_api(prompt, system_prompt)


class FallbackAIProvider(BaseAIProvider):
    """
    Guaranteed local rule-based fallback engine for preschool rhymes, metadata & storyboards.
    Never fails or requires internet.
    """

    def generate_json(self, prompt: str, system_prompt: str = "") -> Optional[Dict[str, Any]]:
        # This will be fulfilled by specialized fallback generators in planner and content modules
        return None

    def generate_text(self, prompt: str, system_prompt: str = "") -> Optional[str]:
        return "Preschool AI Fallback Generated Text"


def get_ai_provider() -> BaseAIProvider:
    """
    Factory function: Returns configured AI provider based on environment variables.
    Cascades gracefully: Configured Provider -> Claude -> OmniRoute -> Ollama -> Fallback.
    """
    preferred = os.environ.get("AI_PROVIDER", "").strip().lower()

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
