from pydantic import BaseModel


class MemberBase(BaseModel):
    name: str
    email: str
    phone: str | None = None
    active: bool = True


class MemberResponse(MemberBase):
    id: int

    class Config:
        from_attributes = True
