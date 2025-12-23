import asyncio
import json
from typing import Optional
import aiohttp
from src.config import settings
from pydantic import BaseModel, Field

class OllamaConfig(BaseModel):
    base_url: str = Field(default=settings.LLM_BASE_URL)
    model: str = Field(default=settings.LLM_MODEL)
    timeout: int = Field(default=settings.LLM_TIMEOUT)
    temperature: float = Field(default=settings.LLM_TEMPERATURE)
    max_tokens: int = Field(default=settings.LLM_MAX_TOKENS)


class OllamaClient:
    def __init__(self, config: OllamaConfig):
        self.config = config
        self.api_url = f"{config.base_url}/api/generate"
        self.health_url = f"{config.base_url}/api/tags"

    async def generate(self, prompt: str, format: str = "json") -> Optional[str]:
        request_data = {
            "model": self.config.model,
            "prompt": prompt,
            "stream": False,
            "format": format,
            "options": {
                "temperature": self.config.temperature,
                "num_predict": self.config.max_tokens
            }
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.api_url,
                    json=request_data,
                    timeout=aiohttp.ClientTimeout(total=self.config.timeout)
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise OllamaError(f"HTTP {response.status}: {error_text}")

                    result = await response.json()
                    return result.get("response", "").strip()

        except aiohttp.ClientError as e:
            raise OllamaError(f"Ошибка сети: {str(e)}")
        except asyncio.TimeoutError:
            raise OllamaError("Таймаут запроса")

    async def health_check(self) -> bool:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.health_url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                    return response.status == 200
        except Exception:
            return False


class OllamaError(Exception):
    pass


def extract_json_from_text(text: str) -> str:
    start = text.find('{')
    end = text.rfind('}') + 1

    if start != -1 and end != 0:
        json_text = text[start:end]
        json.loads(json_text)
        return json_text

    raise ValueError("Не найден валидный JSON в ответе")
