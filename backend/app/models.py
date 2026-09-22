from datetime import datetime
from decimal import Decimal
from typing import Any, Literal
from pydantic import BaseModel, Field, ConfigDict


class LoginRequest(BaseModel):
    officer_id: str = Field(min_length=2, max_length=80)
    password: str = Field(min_length=1, max_length=200)


class RegisterRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=150)
    officer_id: str | None = Field(default=None, max_length=80)
    email: str = Field(min_length=5, max_length=254)
    department: str = Field(min_length=2, max_length=150)
    designation: str = Field(min_length=2, max_length=100)
    password: str = Field(min_length=8, max_length=200)
    confirm_password: str = Field(min_length=8, max_length=200)
    authorized: bool = False


class QueryRequest(BaseModel):
    question: str = Field(min_length=2, max_length=2000)
    mode: Literal["Natural Language Query", "SQL Mode"] = "Natural Language Query"
    parameters: dict[str, Any] = Field(default_factory=dict)


class ReviewRequest(BaseModel):
    action: Literal["ACCEPT", "FLAG", "DISMISS"]
    notes: str = Field(default="", max_length=5000)
    entity_id: str | None = None
    officer_id: str | None = None
    synthesis_id: str | None = None


class CaseCreate(BaseModel):
    case_reference: str = Field(min_length=2, max_length=100)
    title: str = Field(min_length=2, max_length=300)
    status: str = "OPEN"
    incident_time: datetime | None = None
    incident_location_id: int | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class CaseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    case_reference: str
    title: str
    status: str
    opened_at: datetime
    incident_time: datetime | None = None
