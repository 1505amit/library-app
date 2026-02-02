from pydantic import BaseModel


class MemberBase(BaseModel):
    name: str
    email: str
    phone: str | None = None


class MemberResponse(MemberBase):
    id: int
    active: bool

    class Config:
        from_attributes = True
