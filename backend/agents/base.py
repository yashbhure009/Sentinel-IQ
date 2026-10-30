"""Base class for all SentinelIQ agents."""
from abc import ABC, abstractmethod


class BaseAgent(ABC):
    name: str = "base_agent"
    description: str = ""
    is_real: bool = False

    @abstractmethod
    def run(self, context: dict) -> dict:
        ...

    def info(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "is_real": self.is_real,
        }
