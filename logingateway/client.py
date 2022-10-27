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
        reconnect: int = 0,
        **options
    ):
        self.io = socketio.AsyncClient(reconnection_attempts=reconnect, reconnection=True, reconnection_delay=5)
        self.io.on("*", self.recieve_event)
        self.io.on("connect_error", self.connect_error)

        if not options.get("gateway_url") is None:
            self.URL = options.get("gateway_url")

        if not options.get("login_url") is None:
            self.URL_LOGIN = options.get("login_url") 

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

    async def connect_error(namespace: str, data: dict):
        raise Exception(data["message"])

    async def callback(self, event: str, data):
        func: Callable = self.__decorector[event] if event in self.__decorector else self.null
        if not asyncio.iscoroutinefunction(func):
            return

        asyncio.ensure_future(func(data))

    async def null(self):
        return

    def ready(self, cb: Callable = None):
        def _callback(func: Callable):
            self.__decorector["ready"] = func
            return func

        if cb:
            self.__decorector["ready"] = cb
            return 

        return _callback

    def player(self, cb: Callable = None):
        def _callback(func: Callable):
            self.__decorector["player"] = func
            return func

        if cb:
            self.__decorector["player"] = cb
            return 
        
        return _callback

    def error(self, cb: Callable = None):
        def _callback(func: Callable):
            self.__decorector["connect_error"] = func
            return func

        if cb:
            self.__decorector["connect_error"] = cb
            return 
            
        return _callback

    def disconnect(self, cb: Callable = None):
        def _callback(func: Callable):
            self.__decorector["disconnect"] = func
            return func

        if cb:
            self.__decorector["disconnect"] = cb
            return 

        return _callback

    def start(self):
        asyncio.ensure_future(self._start())

    async def _start(self):
        await self.io.connect(self.URL, auth={
            "clientId": self.__client_id,
            "token": encodeToken(self.__client_id, self.__client_secret)
        })
        await self.io.wait()
