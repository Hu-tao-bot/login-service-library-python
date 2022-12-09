import aiohttp


from ..exception import ERRORS
from ..exception import (
    LoginRequired
)
from ..utils import createOffsetPage
from ..model.account import AccountHistoryToken, AccountCookieToken
from ..model.service import ServiceInfo

def login_required(f):
    def decorector(self, **kwargs):
        if self.token == "" or self.token is None:
            raise LoginRequired("You must require login first.")
        return f(self, **kwargs)

    return decorector

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
                timeout=aiohttp.ClientTimeout(10),
                connector=aiohttp.TCPConnector(verify_ssl=False)
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
        headers = {}
        if self.token != "":
            headers["Authorization"] = "Bearer %s" % self.token

        response = await self.session.request(method, f"{self.API_URL}/{url}", headers=headers, **kwargs)
        _json = await response.json()

        code = _json.get("code")
        message = _json.get("message")
        data = _json.get("data")

        # Check if data is unauthorized
        if code == 401:
            await self.login()
            return await self.request(url, method, **kwargs)

        if code != 0:
            return await self.raise_error(code, message=message)

        return data

    @login_required
    async def get_service_info(self):
        resp = await self.request("user/service/info") 
        return ServiceInfo.parse_obj(resp)

    @login_required
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

    @login_required
    async def reload_new_cookie(self, user_id: str, token: str, show_token: bool = True):
        resp = await self.request("accounts/cookie/reload", "POST", json={
            "user_id": user_id,
            "token": token,
            "show_token":show_token
        })
        return AccountCookieToken.parse_obj(resp)

    async def login(self):
        data = await self.request("login/token", auth=aiohttp.BasicAuth(
            login=self.__client_id,
            password=self.__client_secret
        ))

        self.token = data["token"]
        return True
            
    async def raise_error(self, code: int, message: str):
        err = ERRORS.get(code, None)
        if err is None and code != 200:
            raise Exception(code)
        
        raise err(message or "")
