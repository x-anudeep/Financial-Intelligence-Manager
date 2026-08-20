from app.settings import settings
import httpx


class LLMClient:
    system_prompt = (
        "You are a financial analyst assistant for a student/intern demo project. "
        "Keep explanations simple and practical. Explain only the validated structured "
        "financial findings and retrieved document context provided by the application. "
        "Do not calculate ratios, imply fraud, make investment recommendations, or invent document support."
    )

    @property
    def provider(self) -> str:
        configured = settings.llm_provider.lower().strip()
        if configured in {"openai", "gemini"}:
            return configured
        if settings.gemini_api_key:
            return "gemini"
        if settings.openai_api_key:
            return "openai"
        return "none"

    @property
    def enabled(self) -> bool:
        return self.provider in {"openai", "gemini"}

    def complete(self, prompt: str) -> str:
        if not self.enabled:
            return ""
        if self.provider == "gemini":
            return self._complete_gemini(prompt)
        return self._complete_openai(prompt)

    def _complete_openai(self, prompt: str) -> str:
        if not settings.openai_api_key:
            return ""
        try:
            response = httpx.post(
                "https://api.openai.com/v1/responses",
                headers={
                    "Authorization": f"Bearer {settings.openai_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": settings.openai_model,
                    "input": [
                        {
                            "role": "system",
                            "content": self.system_prompt,
                        },
                        {"role": "user", "content": prompt},
                    ],
                    "max_output_tokens": 500,
                },
                timeout=20,
            )
            response.raise_for_status()
            payload = response.json()
            text = payload.get("output_text")
            if text:
                return str(text)
            output = payload.get("output") or []
            parts: list[str] = []
            for item in output:
                for content in item.get("content", []):
                    if content.get("type") in {"output_text", "text"} and content.get("text"):
                        parts.append(content["text"])
            return "\n".join(parts).strip()
        except Exception:
            return ""

    def _complete_gemini(self, prompt: str) -> str:
        if not settings.gemini_api_key:
            return ""
        try:
            response = httpx.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/{settings.gemini_model}:generateContent",
                params={"key": settings.gemini_api_key},
                json={
                    "systemInstruction": {"parts": [{"text": self.system_prompt}]},
                    "contents": [{"role": "user", "parts": [{"text": prompt}]}],
                    "generationConfig": {"maxOutputTokens": 500, "temperature": 0.2},
                },
                timeout=20,
            )
            response.raise_for_status()
            payload = response.json()
            parts: list[str] = []
            for candidate in payload.get("candidates", []):
                for part in candidate.get("content", {}).get("parts", []):
                    if part.get("text"):
                        parts.append(str(part["text"]))
            return "\n".join(parts).strip()
        except Exception:
            return ""


llm_client = LLMClient()
