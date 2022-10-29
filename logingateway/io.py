"""
The MIT License (MIT)

Copyright (c) 2015-present Miguel Grinberg
Copyright (c) 2022-present Hu Tao bot

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import asyncio
import logging
import engineio

from typing import Any, Callable, Dict

from .exception import Unauthorized
from .packet import Packet
from .packet import (
    CONNECT,
    DISCONNECT,
    EVENT,
    CONNECT_ERROR
)

__all__ = ('GatewayIO',)

class GatewayIO(object):
    """
        ## GatewayIO
        ---
        Monify from `python-socketio`

        ## Example use
        ```
        eio = GatewayIO()

        @eio.event()
        async def ready(data):
            print("READY")
            print(data)

        @eio.event()
        async def player(data):
            print("PLAYER")
            print(data)

        async def start_client():
            await eio.start("http://localhost:8090")
            await eio.wait()
        ```

    """

    def __init__(
        self,
        reconnect: bool = True
    ) -> None:
        self.reconnect = reconnect
        self.connected = False

        self.eio = engineio.AsyncClient()
        self.eio.on('connect', self._handle_connect)
        self.eio.on('message', self._handle_message)
        self.eio.on('disconnect', self._handle_disconnect)

        self.log = logging.getLogger(__name__)

        self.__func: Dict[str, Callable] = {}

        self.__host = 'http://localhost'
        self.__auth = {}
        self._reconnect_task: asyncio.Task = None
        self._reconnect_abort: asyncio.Event = None

    async def start(
        self,
        host: str = '',
        auth: Dict[str, Any] = {}
    ):
        if host != "":
            self.__host = host

        if auth:
            self.__auth = auth

        while not self.connected:
            try:
                await self.eio.connect(self.__host, engineio_path="/socket.io")
                self.connected = True
            except engineio.exceptions.ConnectionError:
                self.log.error("Failed to connect " +
                               self.__host + " Retrying...")
                self.connected = False
                await self.sleep(1)

    async def disconnect(self):
        await self._send_packet(Packet(DISCONNECT))
        await self.eio.disconnect(abort=True)
        self.log.warning("Disconnect from SocketIO server")

    def event(self):
        def decorector(func: Callable):
            self.__func[func.__name__] = func
            return func

        return decorector

    def on(self, name: str, func: Callable):
        if name != "":
            self.__func[name] = func
        else:
            self.__func[func.__name__] = func

    async def _handle_connect(self):
        self.log.info("Connected to EngineIO Server")
        self.log.info("Verifying key")
        # Connect data
        await self._send_packet(Packet(CONNECT, self.__auth))

    async def _handle_message(self, data):
        pkt = Packet(encoded_packet=data)
        if pkt.packet_type == CONNECT:
            self.log.info("Connected to SocketIO succuss")
            await self.func("connect")

        if pkt.packet_type == CONNECT_ERROR:
            self.log.info("Disconnected to SocketIO")
            if not await self.func("connect_error"):
                raise Unauthorized(pkt.data["message"])
            await self.disconnect()

        if pkt.packet_type == EVENT:
            event_name = pkt.data[0]
            event_data = pkt.data[1]

            if "*" in self.__func:
                await self.func("*", event_name, event_data)

            await self.func(event_name, event_data)

    async def _handle_disconnect(self):
        if self.connected:
            self.connected = False
        if self.eio.state == 'connected':
            self._reconnect_task = self.eio.start_background_task(self.start)

    async def _send_packet(self, packet: Packet):
        pkt = packet.encode()
        if isinstance(pkt, list):
            for ep in pkt:
                await self.eio.send(ep)
        else:
            await self.eio.send(pkt)

    async def func(self, name: str, *args, **kwargs):
        if name in self.__func:
            asyncio.ensure_future(self.__func[name](*args, **kwargs))
            return True
        else:
            return False

    async def sleep(self, sec: int = 1):
        return await self.eio.sleep(sec)

    async def wait(self):
        while True:
            await self.eio.wait()
            await self.sleep(1)
            if not self._reconnect_task:
                break
            await self._reconnect_task
            if self.eio.state != 'connected':
                break
