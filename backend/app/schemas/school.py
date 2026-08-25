from pydantic import BaseModel, ConfigDict

from app.db.models import SchoolSource


class SchoolOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    zone: str
    lat: float
    lon: float
    source: SchoolSource
