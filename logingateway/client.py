import asyncio
import hashlib
import urllib.parse

from datetime import datetime
from typing import Any, Callable

from .gateway import HuTaoGateway
from .api import HuTaoLoginRESTAPI

from .model import Player, Ready
from .callback import Callback

__all__ = ("HuTaoLoginAPI",)


class HuTaoLoginAPI(Callback):
    URL: str = "https://hutao-login-gateway.m307.dev"
    URL_LOGIN: str = "https://hutao-login.m307.dev"
    URL_API: str = "https://hutao-login-api.m307.dev/api/v0"

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        **options
    ):
        super().__init__()

        if not options.get("gateway_url") is None:
            self.URL = options.get("gateway_url")

        if not options.get("login_url") is None:
            self.URL_LOGIN = options.get("login_url")

        if not options.get("api_url") is None:
            self.URL_API = options.get("api_url")

        self.__client_id = client_id
        self.__client_secret = client_secret

        self.gateway = HuTaoGateway(
            client_id=self.__client_id,
            client_secret=self.__client_secret,
            gatewayURL=self.URL
        )
        self.gateway.on(-1, self.__disconnect)
        self.gateway.on(101, self.__ready)
        self.gateway.on(102, self.__recieve_event)
        self.gateway.on(103, self.__recieve_event)

        self.api = HuTaoLoginRESTAPI(
            client_id=self.__client_id,
            client_secret=self.__client_secret,
            apiURL=self.URL_API
        )

    def generate_login_url(
        self,
        user_id: str,
        guild_id: str,
        channel_id: str,
        message_id: str = '',
        language: str = 'en',
    ):
        """
            RAW DATA:
            Client ID + Client Secret + GuildID + ChannelID + MessageID + UserID + Timestamp
        """
        ts = round(datetime.now().timestamp())

        token = hashlib.sha256("".join([
            self.__client_id,
            self.__client_secret,
            guild_id,
            channel_id,
            message_id,
            user_id,
            str(ts)
        ]).encode()).hexdigest()
        query = urllib.parse.urlencode({
            "ts": ts,
            "client_id": self.__client_id,
            "id": user_id,
            "guild": guild_id,
            "channel": channel_id,
            "message": message_id,
            "language": language,
            "token": token
        })

        return self.URL_LOGIN + "/?" + query, token

    async def __ready(self, data: Any = None):
        await self.callback("ready", Ready.parse_obj(data)) 

    async def __disconnect(self, data: Any = None):
        await self.callback("disconnect", None) 

    async def __recieve_event(self, data: Any = None):
        t = data.get("type").lower()
        d = data.get("data")

        if t is None:
            return

        if t in ["player_register", "player_update"]:
            data = Player.parse_obj(d)
        else:
            data = d
        
        await self.callback(t, data)

    async def callback(self, event: str, data):
        func: Callable = self.DECORECTOR[event] if event in self.DECORECTOR else self.null
        if not asyncio.iscoroutinefunction(func):
            return
        asyncio.ensure_future(func(data))

    async def null(self, *args, **kwargs):
        return

    def start(self):
        asyncio.ensure_future(self._start())

    async def _start(self):
        await self.api.login()
        await self.gateway._start()
