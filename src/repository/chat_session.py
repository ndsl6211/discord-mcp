from abc import ABC
from dataclasses import asdict, dataclass
import json
from typing import Any, Dict, List, Literal

from openai.types.responses import EasyInputMessageParam


@dataclass
class Record:
    user_id: str
    role: Literal["user", "assistant", "system", "developer"]
    message: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Record":
        return cls(**data)


@dataclass
class ChatSession:
    id: int
    history: List[Record]

    def get_history(self) -> List[EasyInputMessageParam]:
        return [
            EasyInputMessageParam(
                content=record.message,
                role=record.role,
                type="message"
            )
            for record in self.history
        ]


class ChatSessionStorage(ABC):
    def create_session(self, session_id: int, system_prompt: str | None) -> ChatSession:
        raise NotImplementedError

    def add_message(
        self,
        session_id: int,
        record: Record,
    ) -> None:
        raise NotImplementedError

    def get_session(self, session_id: int) -> ChatSession | None:
        raise NotImplementedError

    def get_all_sessions(self) -> Dict[int, ChatSession]:
        raise NotImplementedError
