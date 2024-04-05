from pydantic import BaseModel


class ClientHandshake(BaseModel):
    ip_addr: str
    port: int
    indeks: int
