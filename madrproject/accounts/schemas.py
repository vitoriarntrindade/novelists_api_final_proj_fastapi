from pydantic import BaseModel, EmailStr


class AccountSchema(BaseModel):
    username: str
    email: EmailStr
    password: str


class AccountPublicSchema(BaseModel):
    id: int
    username: str
    email: EmailStr


class ListAccountsSchema(BaseModel):
    accounts: list[AccountPublicSchema]
