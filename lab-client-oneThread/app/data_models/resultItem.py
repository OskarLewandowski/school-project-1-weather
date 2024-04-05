from pydantic import BaseModel

class ResultItem(BaseModel):
    day: int

    HUM_MIN: float
    HUM_MAX: float
    HUM_MEAN: float
    HUM_MEDIAN: float

    TEMP_MIN: float
    TEMP_MAX: float
    TEMP_MEAN: float
    TEMP_MEDIAN: float

    LIGHT_MIN: float
    LIGHT_MAX: float
    LIGHT_MEAN: float
    LIGHT_MEDIAN: float

    PRESS_MIN: float
    PRESS_MAX: float
    PRESS_MEAN: float
    PRESS_MEDIAN: float

    PREC_MIN: float
    PREC_MAX: float
    PREC_MEAN: float
    PREC_MEDIAN: float

