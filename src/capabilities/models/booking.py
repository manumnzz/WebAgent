from datetime import date, time, datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

Weekday = Literal[
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday"
]

class BookingService(BaseModel):
    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    duration_minutes: int = Field(gt=0)

class BookingServiceDraft(BaseModel):
    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    duration_minutes: int | None = Field(
        default=None,
        gt=0,
    )

class PendingArrivalType(BaseModel):
    id: str = Field(min_length=1)
    name: str = Field(min_length=1)

class InquiryType(BaseModel):
    id: str = Field(min_length=1)
    name: str = Field(min_length=1)

class BookingConfigurationDraft(BaseModel):
    timezone: str | None = None

    services: list[BookingServiceDraft] = Field(
        default_factory=list
    )
    pending_arrival_types: list[PendingArrivalType] = Field(default_factory=list)
    inquiry_types: list[InquiryType] = Field(default_factory=list)

    weekly_schedule: list[BookingDaySchedule] | None = None

    slot_interval_minutes: int | None = Field(
        default=None,
        gt=0,
    )

class BookingMissingInformation(BaseModel):
    service_durations: list[str] = Field(
        default_factory=list
    )

    timezone: bool = False
    weekly_schedule: bool = False
    slot_interval_minutes: bool = False

    @property
    def is_complete(self) -> bool:
        return (
            not self.service_durations
            and not self.timezone
            and not self.weekly_schedule
            and not self.slot_interval_minutes
        )

class BookingCollectedInformation(BaseModel):
    service_durations: dict [str, int] = Field(
        default_factory=dict
    )
    appointment_modes: dict[str, Literal["pending_arrival", "inquiry"]] = Field(
        default_factory=dict
    )

    @field_validator("service_durations")
    @classmethod
    def validate_durations(cls, durations: dict[str, int]) -> dict[str, int]:
        if any(minutes <= 0 for minutes in durations.values()):
            raise ValueError("Las duraciones deben ser mayores que cero.")
        return durations

    timezone: str | None = None

    weekly_schedule: list[BookingDaySchedule] | None = None

    slot_interval_minutes: int | None = Field(
        default=None,
        gt=0,
    )

class BookingBusinessInfo(BaseModel):
    name: str | None = None
    phone: str | None = None
    whatsapp: str | None = None
    email: str | None = None
    address: str | None = None

class BookingTimeRange(BaseModel):
    start: time
    end: time

    @model_validator(mode="after")
    def validate_time_range(self):
        if self.end <= self.start:
            raise ValueError(
                "La hora de fin debe ser posterior a la hora de inicio."
            )

        return self

class BookingDaySchedule(BaseModel):
    weekday: Weekday
    ranges: list[BookingTimeRange]

class BookingConfiguration(BaseModel):
    timezone: str = Field(min_length=1)

    services: list[BookingService] = Field(default_factory=list)
    pending_arrival_types: list[PendingArrivalType] = Field(default_factory=list)
    inquiry_types: list[InquiryType] = Field(default_factory=list)
    weekly_schedule: list[BookingDaySchedule] = Field(default_factory=list)
    
    business: BookingBusinessInfo | None = None

    slot_interval_minutes: int = Field(
        default=30,
        gt=0
    )

class BookingRequest(BaseModel):
    first_name: str = Field(min_length=1)
    last_name: str = Field(min_length=1)

    email: str | None = None
    phone: str | None = None 

    service_id: str = Field(min_length=1)

    booking_date: date
    booking_time: time

    notes: str | None = None

    @model_validator(mode="after")
    def validate_contact(self):
        if not self.email and not self.phone:
            raise ValueError(
                "La reserva necesita almenos un email o un teléfono de contacto."
            )

        return self


class PendingArrivalRequest(BookingRequest):
    notes: str = Field(min_length=1)

    @field_validator("notes")
    @classmethod
    def validate_reason(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Indica el motivo de la visita.")
        return value.strip()


class InquiryRequest(BaseModel):
    first_name: str = Field(min_length=1)
    last_name: str = Field(min_length=1)
    email: str | None = None
    phone: str | None = None
    service_id: str = Field(min_length=1)
    notes: str = Field(min_length=1)

    @model_validator(mode="after")
    def validate_inquiry(self):
        if not self.email and not self.phone:
            raise ValueError("Indica un email o teléfono de contacto.")
        if not self.notes.strip():
            raise ValueError("Indica el motivo de la consulta.")
        self.notes = self.notes.strip()
        return self

class CalendarBusyInterval(BaseModel):
    start: datetime
    end: datetime

    @model_validator(mode="after")
    def validate_interval(self):
        if self.start.tzinfo is None or self.end.tzinfo is None:
            raise ValueError(
                "Los intervalos ocupados deben incluir zona horaria."
            )

        if self.end <= self.start:
            raise ValueError(
                "El final del intervalo debe ser posterior al inicio."
            )

        return self

