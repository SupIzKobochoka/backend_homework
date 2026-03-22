from pydantic import BaseModel, StrictBool, StrictInt, StrictStr


class Account(BaseModel):
    id: StrictInt
    login: StrictStr
    password: StrictStr
    is_blocked: StrictBool


class LoginRequest(BaseModel):
    login: StrictStr
    password: StrictStr
