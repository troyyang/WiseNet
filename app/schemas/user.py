from pydantic import Field
from . import BaseViewModel
from pydantic import EmailStr
from datetime import datetime

class UserCreate(BaseViewModel):
    username: str = Field(max_length=200)
    email: EmailStr | None = Field(default=None, max_length=200)
    mobile: str | None = Field(default=None, max_length=20)
    password: str | None = Field(default=None, max_length=32)

class UserSecuritySetting(BaseViewModel):
    org_password: str = Field(max_length=32)
    new_password: str = Field(max_length=32)
    confirm_password: str = Field(max_length=32)

class UserLogin(BaseViewModel):
    username: str = Field(max_length=200)
    password: str = Field(max_length=32)

class UserList(BaseViewModel):
    keyword: str | None = Field(default=None)
    role: str | None = Field(default=None)
    # start_time: datetime = Field(default=None)
    # end_time: datetime = Field(default=None)
    current: int = Field(default=1)
    page_size: int = Field(default=10)