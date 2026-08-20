
from app.cache.base import CacheBackend


class ChatCache:

    PREFIX = "chat"
    DEFAULT_TTL = 60 * 60 * 24
    MAX_MESSAGES = 20

    def __init__(self,cache: CacheBackend,):
        self.cache = cache

    # ==================================================
    # Key
    # ==================================================

    def _key(self,user_id: int,chat_id: int,) -> str:

        return ( f"user:{user_id}:" f"chat:{chat_id}:messages")

    # ==================================================
    # GET HISTORY
    # ==================================================

    def get_history(self,user_id: int,chat_id: int,) -> list[dict]:

        return (self.cache.get(self._key(user_id,chat_id,))or [])

    # ==================================================
    # ADD MESSAGE
    # ==================================================

    def add_message(self,user_id: int,chat_id: int,role: str,content: str,) -> None:

        messages = self.get_history(user_id,chat_id,)

        messages.append(
            {"role": role,
                "content": content,
            }
        )

        messages = messages[-self.MAX_MESSAGES:]

        self.cache.set(self._key(user_id,chat_id,),messages,ttl=self.DEFAULT_TTL,)

    # ==================================================
    # SET HISTORY
    # ==================================================

    def set_history(self,user_id: int,chat_id: int,messages: list[dict],) -> None:

        self.cache.set(
           self._key(
                user_id,
                chat_id,
            ),
            messages[-self.MAX_MESSAGES:],
            ttl=self.DEFAULT_TTL,
        )

    # ==================================================
    # CLEAR CHAT
    # ==================================================

    def clear(self,user_id: int,chat_id: int,) -> None:
        self.cache.delete(
            self._key(
                user_id,
                chat_id,
            )
        )