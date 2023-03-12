import aiohttp
import asyncio
import json
import logging

from typing import Any, Callable, Union
from aiohttp.client_exceptions import (
    ClientConnectionError
)
from aiohttp import (
    WSCloseCode,
    WSServerHandshakeError
)

from .utils import encodeToken
from .exception import RetryTimeout

LOGGER = logging.getLogger(__name__)

class HuTaoGateway:
    """
    # Hutao Login Gateway
    ----
    ## Status code (Server):
    - 100: Connected to server
    - 101: Login success
    - 102: Recieved new message (Please refer in "type" in "d")
    - 103: Logout account

    ## Status code (Library):
    - -1: Disconnected
    """
    session: aiohttp.ClientSession = None
    ws: aiohttp.ClientWebSocketResponse = None

    # URL
    GATEWAY_URL: str = "https://hutao-login-gateway.m307.dev"

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        gatewayURL: str = "https://hutao-login-gateway.m307.dev",
        retry_connect: int = 0, 
    ) -> None:

        # URL
        self.GATEWAY_URL = gatewayURL

        # Authenication
        self.__client_id = client_id
        self.__client_secret = client_secret

        # Callback
        self.__callback = {}

        # Settings
        self.__retry = retry_connect
        self.__retry_count = 0

        # System
        self.__closed = False
        self.__stop_heartbeat = True

    async def close(self):
        if not self.session is None:
            await self.session.close()
            self.__closed = True
            self.__stop_heartbeat = True

            await self.__cb(-1)
    
    def start(self):
        asyncio.ensure_future(self._start())

    def on(self, code: int, cb: Callable):
        self.__callback[code] = cb

    async def logout(self):
        await self.ws.send_json({
            "c": 1001,
            "d": None
        })

    async def _start(self):
        # Check if aiohttp start?
        if self.session is None:
            self.session = aiohttp.ClientSession()

        while not self.__closed:
            # Connect to Websocket
            try:
                if self.ws is None:
                    self.ws = await self.session.ws_connect(self.GATEWAY_URL)

                # Wating recieved new message (Timeout 60 seconds)
                async for data in self.ws:
                    if data.type is aiohttp.WSMsgType.TEXT:
                        await self.recived_message(data.data)
                    if data.type is aiohttp.WSMsgType.ERROR:
                        LOGGER.error("Got error from server. Please read in this error")
                        LOGGER.error(exc)

            except asyncio.CancelledError:
                await self.close()
                break
            except (WSServerHandshakeError, OSError) as e:
                self.__stop_heartbeat = True
                if isinstance(e, ClientConnectionError) or \
                    isinstance(e, WSServerHandshakeError):
                    LOGGER.error("Server has down or connection failed. Retrying ....")

                    # Delay
                    if(self.__retry_count <= 10):
                        self.__retry_count += 1 

                    if self.__retry == self.__retry_count:
                        raise RetryTimeout("Retry has timeout")

                    await asyncio.sleep(1 + self.__retry_count * 2)
            except Exception as exc:
                # Some another error 
                LOGGER.error(exc)
            finally:
                if not self.ws is None:
                    await self.close()
                
    async def recived_message(self, raw: Any):
        # Format JSON
        data = json.loads(raw)

        LOGGER.debug("New data from server: %s" % raw)

        status_code = data.get("c", -1)
        info = data.get("d", None)
        
        # Callback
        await self.__cb(status_code, info)
            
        # Check data
        if status_code == 100: # Connected
            LOGGER.debug("Authentication...")
            # Heartbeath
            asyncio.ensure_future(self.__heartbeat(info["interval"] / 1000 or 45))
            await self.ws.send_json({
                "c": 1000,
                "d": {
                    "clientId": self.__client_id,
                    "token": encodeToken(self.__client_id, self.__client_secret)
                }
            })
            
        if status_code == 103: # Logout success
            LOGGER.info("Logout success")
            # Close session
            await self.close()

    async def __cb(self, event_name: Union[str, int], data = None):
        # Callback
        coro = self.__callback.get(event_name)
        if coro:
            asyncio.ensure_future(coro(data))

    async def __heartbeat(self, interval: int = 45):
        LOGGER.info("Heartbeat has start")
        self.__stop_heartbeat = False
        while not self.__closed:
            await asyncio.sleep(interval)
            if not self.__stop_heartbeat:
                try:
                    await self.ws.send_json({
                        "c": 1,
                        "d": None
                    })
                except:
                    break
            else:
                break
            