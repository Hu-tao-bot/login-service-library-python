import pydantic

from enum import Enum
from typing import Union, Any

__all__ = ("LoginMethod", "ServerId", "Discord",
           "Client", "Ready", "Genshin", "Player")


class LoginMethod(str, Enum):
    UNKNOWN = "unknown"
    TOKEN = "token"
    EMAIL = "mail"
    UID = "uid"
    HOYOLAB_ID = "hoyolab_id"
    AUTHKEY = "authkey"
    MOBILE = "mobile"

class ServerId(str, Enum):
    OVERSEA = "os"
    CHINA = "cn"

class GameId(str, Enum):
    UNKNOWN = ""
    HONKAI_IMPACT = "H3D",
    GENSHIN_IMPACT = "GI"
    HONKAI_STAR_RAIL = "HSR"


class Discord(pydantic.BaseModel):
    user_id: str
    guild_id: str = ''
    channel_id: str = ''
    message_id: Union[str, None] = ''


class Client(pydantic.BaseModel):
    id: str
    name: str

class ClientProfile(pydantic.BaseModel):
    name: str = ''
    image: str = ''
    created_at: str = ''
    locate: Union[str, None] = ''
    color: Union[str, None] = ''

class Ready(pydantic.BaseModel):
    id: int
    client_id: str = ''
    username: str = ''
    profile: ClientProfile

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)
        
        self.username = data["profile"]["name"]

class Genshin(pydantic.BaseModel):
    id: int = 0
    game: GameId = GameId.UNKNOWN
    userid: str = ''
    ltuid: str = ''
    ltoken: str = ''
    cookie_token: str = ''
    uid: str = ''
    login_type: LoginMethod
    server: ServerId

class Player(pydantic.BaseModel):
    token: str = ''
    discord: Discord
    client: Client
    genshin: Genshin
