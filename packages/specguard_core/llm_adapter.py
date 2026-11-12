"""Dual-Mode LLM Adapter supporting OpenAI-compatible Live endpoints (Qwen3, DeepSeek) + Deterministic Fallback."""

from __future__ import annotations

import json
import os
import urllib.request
from typing import Any, Dict, Literal, Optional


class LLMAdapter:
    """Provides optional live LLM enrichment while guaranteeing 100% deterministic offline operation."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
    ) -> None:
        self.api_key = api_key or os.environ.get("SPECGUARD_LLM_API_KEY", "").strip()
        self.base_url = (
            base_url
            or os.environ.get("SPECGUARD_LLM_BASE_URL", "https://api.deepseek.com/v1").strip()
        ).rstrip("/")
        self.model = model or os.environ.get("SPECGUARD_LLM_MODEL", "deepseek-chat").strip()

    @property
    def mode(self) -> Literal["live_api", "deterministic_rule_engine"]:
        return "live_api" if bool(self.api_key) else "deterministic_rule_engine"

    def complete_json(
        self,
        system_prompt: str,
        user_prompt: str,
        fallback_payload: Dict[str, Any],
        timeout_sec: float = 8.0,
    ) -> Dict[str, Any]:
        """Attempt live OpenAI-compatible JSON completion if configured; otherwise return verified fallback."""
        if not self.api_key:
            return fallback_payload

        try:
            url = f"{self.base_url}/chat/completions"
            body = json.dumps(
                {
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    "temperature": 0.0,
                    "response_format": {"type": "json_object"},
                }
            ).encode("utf-8")
            req = urllib.request.Request(
                url,
                data=body,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}",
                    "User-Agent": "SpecGuard-Crew/0.1.0",
                },
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                content = data["choices"][0]["message"]["content"]
                parsed = json.loads(content)
                if isinstance(parsed, dict):
                    return parsed
        except Exception:
            # Never fail verification if an external API times out or is unreachable
            pass

        return fallback_payload
