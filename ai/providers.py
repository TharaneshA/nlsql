from enum import Enum
from typing import Dict, Optional

class AIProvider(Enum):
    GEMINI = "gemini"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GROK = "grok"

class ProviderConfig:
    def __init__(self, name: str, api_key: str = "", model: str = ""):
        self.name = name
        self.api_key = api_key
        self.model = model

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key)

    def to_dict(self) -> Dict[str, str]:
        return {
            "name": self.name,
            "api_key": self.api_key,
            "model": self.model
        }

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> 'ProviderConfig':
        return cls(
            name=data.get("name", ""),
            api_key=data.get("api_key", ""),
            model=data.get("model", "")
        )

DEFAULT_MODELS = {
    AIProvider.GEMINI: "gemini-2.0-flash",
    AIProvider.OPENAI: "gpt-4",
    AIProvider.ANTHROPIC: "claude-3-opus",
    AIProvider.GROK: "grok-1"
}

def get_default_model(provider: AIProvider) -> str:
    return DEFAULT_MODELS.get(provider, "")