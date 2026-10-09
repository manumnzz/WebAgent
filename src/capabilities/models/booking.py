from datetime import date, time, datetime
from typing import Literal

from pydantic import BaseModel, Field, model_validator

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

    services: list[BookingService]
    weekly_schedule: list[BookingDaySchedule]

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

