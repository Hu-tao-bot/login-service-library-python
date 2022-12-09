from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field


class AccountHistoryTokenInfo(BaseModel):
    user_id: str
    login_type: str
    token: str
    created_at: str
    uid: str

class AccountHistoryToken(BaseModel):
    total: int = Field(0, alias="all")
    data: List[AccountHistoryTokenInfo] = Field([], alias="list")

class AccountCookieToken(BaseModel):
    ltuid: str
    cookie_token: str
    server: str
    login_type: str
