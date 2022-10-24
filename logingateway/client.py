import asyncio
import hashlib
import socketio
import urllib.parse

from datetime import datetime
from typing import Any, Callable

from .utils import encodeToken
from .model import Player, Ready

__all__ = ("HuTaoLoginAPI",)


class HuTaoLoginAPI:
    URL: str = "https://hutao-login-gateway.m307.dev"
    URL_LOGIN: str = "https://hutao-login.m307.dev"

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        reconnect: int = 5
    ):
        self.io = socketio.AsyncClient(reconnection_attempts=reconnect)
        self.io.on("*", self.recieve_event)

        self.__decorector = {}

        self.__client_id = client_id
        self.__client_secret = client_secret

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

    async def recieve_event(self, event: str, data: Any = None):
        if event == "player":
            data = Player.parse_obj(data)
        if event == "ready":
            data = Ready.parse_obj(data)

        await self.callback(event, data)

    async def callback(self, event: str, data):
        func: Callable = self.__decorector[event] or self.null
        if not asyncio.iscoroutinefunction(func):
            return

        asyncio.ensure_future(func(data))

    async def null(self):
        return

    def ready(self):
        def callback(func: Callable):
            self.__decorector["ready"] = func
            return func

        return callback

    def player(self):
        def callback(func: Callable):
            self.__decorector["player"] = func
            return func

        return callback

    def error(self):
        def callback(func: Callable):
            self.__decorector["error"] = func
            return func

        return callback

    def disconnect(self):
        def callback(func: Callable):
            self.__decorector["disconnect"] = func
            return func

        return callback

    async def start(self):
        await self.io.connect(self.URL, auth={
            "clientId": self.__client_id,
            "token": encodeToken(self.__client_id, self.__client_secret)
        })
        await self.io.wait()
