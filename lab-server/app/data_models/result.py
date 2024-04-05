from pydantic import BaseModel
from typing import List


class ResultItem(BaseModel):
    day: int

    HUM_COUNT: float
    HUM_MODE: float
    HUM_AVG: float

    TEMP_COUNT: float
    TEMP_MODE: float
    TEMP_AVG: float

    LIGHT_COUNT: float
    LIGHT_MODE: float
    LIGHT_AVG: float

    PRESS_COUNT: float
    PRESS_MODE: float
    PRESS_AVG: float

    PREC_COUNT: float
    PREC_MODE: float
    PREC_AVG: float


class Result(BaseModel):
    ip_addr: str
    port: int
    indeks: int
    aggregates: List[ResultItem]
