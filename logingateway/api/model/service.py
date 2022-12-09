from pydantic import BaseModel

class ServiceLoginAccess(BaseModel):
    token: bool
    mail: bool
    uid: bool
    hoyolab_id: bool
    authkey: bool
    mobile: bool

class ServiceInfo(BaseModel):
    registered_at: str
    client_id: str
    name: str
    default_locate: str
    color: str
    image: str
    login_access: ServiceLoginAccess
    is_supened: bool
    is_production: bool