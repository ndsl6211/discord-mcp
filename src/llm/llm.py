from abc import ABC, abstractmethod

from ..repository.chat_session import ChatSession


class LLMInteractor(ABC):
    @abstractmethod
    async def send_message(self, chat_session: ChatSession) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_name(self) -> str:
        raise NotImplementedError
