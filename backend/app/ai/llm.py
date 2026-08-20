from app.settings import settings


class LLMClient:
    @property
    def enabled(self) -> bool:
        return bool(settings.openai_api_key)

    def complete(self, prompt: str) -> str:
        if not self.enabled:
            return ""
        return "AI provider configured. For this MVP, deterministic structured findings and retrieved source context are returned by the backend."


llm_client = LLMClient()
