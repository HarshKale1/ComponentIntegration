from datetime import date

from pydantic import BaseModel, Field, ConfigDict


class EventImpactRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ticker: str = Field(min_length=1, max_length=20)
    event_date: date
    window_days: int = Field(default=7, ge=1, le=30)
