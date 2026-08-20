from app.settings import settings
import httpx


class LLMClient:
    @property
    def enabled(self) -> bool:
        return bool(settings.openai_api_key)

    def complete(self, prompt: str) -> str:
        if not self.enabled:
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
                            "content": (
                                "You are a financial analyst assistant. Explain only the validated structured "
                                "financial findings and retrieved document context provided by the application. "
                                "Do not calculate ratios, imply fraud, make investment recommendations, or invent document support."
                            ),
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


llm_client = LLMClient()
