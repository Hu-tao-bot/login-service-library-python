import aiohttp

from ..exception import ERRORS
from ..exception import (
    MaximumRetryLogin,
    ConnectServerFailed
)

from ..utils import createOffsetPage
from ..model.account import AccountHistoryToken, AccountCookieToken, AccountToken
from ..model.service import ServiceInfo

class HuTaoLoginRESTAPI:
    session: aiohttp.ClientSession = None

    # API
    API_URL: str = "https://hutao-login-gateway.m307.dev"

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        apiURL: str = "https://hutao-login-api.m307.dev/api/v0"
    ) -> None:
        # URL
        self.API_URL = apiURL

        # Token
        self.token = ''

        # Authenication
        self.__client_id = client_id
        self.__client_secret = client_secret

    def start_session(self):
        if self.session is None:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(10)
            )

    async def close(self):
        if not self.session is None:
            await self.session.close()

    async def __aenter__(self):
        self.start_session()
        return self

    async def __aexit__(
        self, 
        exc_type, 
        exc_value, 
        exc_tb
    ):
        await self.close()

    async def request(self, url: str, method: str = "GET", **kwargs):
        # Set MAX RETRY REQUEST
        MAX_RETRY = 10
        RETRY = 0
        # Start session
        self.start_session()
        
        while RETRY <= MAX_RETRY:
            headers = {}
            if self.token != "" and kwargs.get("auth") is None:
                headers["Authorization"] = "Bearer %s" % self.token

            response = await self.session.request(method, f"{self.API_URL}/{url}", headers=headers, **kwargs)
            _json = await response.json()

            code = _json.get("code")
            message = _json.get("message")
            data = _json.get("data")

            if code != 0 and code >= 1000 and code <= 9999:
                if code in [1020, 1021]:
                    await self.login()
                    continue

                return await self.raise_error(code, message=message)

            if code >= 500 or response.status >= 500:
                raise ConnectServerFailed("Hu Tao login API has down. Please contact to me@m307.dev")

            return data

    async def get_service_info(self):
        resp = await self.request("user/service/info") 
        return ServiceInfo.parse_obj(resp)

    async def get_history_user(self, user_id: str = "", login_type: str = "", page: int = 0) -> AccountHistoryToken:
        offset, limit = createOffsetPage(page)

        payload = {
            "offset": offset,
            "limit": limit   
        }
        query = {}
        if user_id:
            query["query"] = str(user_id)
        if login_type:
            query["login_type"] = str(login_type)

        resp = await self.request("accounts/history/token", "POST", params=query, json=payload)
        return AccountHistoryToken.parse_obj(resp)

    async def resend_token(self, user_id: str, token: str, show_token: bool = True, is_register_event: bool = False):
        resp = await self.request("accounts/history/token/reload", "POST", json={
            "user_id": user_id,
            "token": token,
            "show_token": show_token,
            "is_register": is_register_event
        })
        return AccountToken.parse_obj(resp)

    async def reload_new_cookie(self, user_id: str, token: str, show_token: bool = True):
        resp = await self.request("accounts/cookie/reload", "POST", json={
            "user_id": user_id,
            "token": token,
            "show_token":show_token
        })
        return AccountCookieToken.parse_obj(resp)

    async def login(self):
        MAX_LOGIN = 15
        RETRY = 0
        while RETRY <= MAX_LOGIN:
            data = await self.request("login/token", auth=aiohttp.BasicAuth(
                login=self.__client_id,
                password=self.__client_secret
            ))

            if not data is None:
                self.token = data["token"]
                return True
            
            RETRY += 1
        
        raise MaximumRetryLogin("You maximum to retry login. Please change client_id or client_secret to login again")
            
    async def raise_error(self, code: int, message: str):
        err = ERRORS.get(code, None)
        if err is None and code != 200:
            raise Exception(code)
        
        raise err(message or "")
