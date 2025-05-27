from abc import ABC, abstractmethod


class LLMInteractor(ABC):
    @abstractmethod
    def start_new_chat_session(self, session_id: str) -> None:
        """
        Starts a new chat session with the given session ID.
        """
        raise NotImplementedError

    @abstractmethod
    async def send_message(self, message: str, user_id: str, session_id: str) -> str:
        """
        Sends a message to the LLM and returns the response.
        If the session ID is not known, it should raise an exception.

        Args:
            message (str): The message to send.
            session_id (str): The ID of the chat session.
        """
        raise NotImplementedError

    @abstractmethod
    def get_name(self) -> str:
        """
        Returns the name of the LLM.
        """
        raise NotImplementedError

    @abstractmethod
    def is_known_chat_session(self, session_id: str) -> bool:
        """
        Checks if the given session ID is known.
        """
        raise NotImplementedError
