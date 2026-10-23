from datetime import date, datetime, timedelta

from capabilities.booking.calendar_provider import (
    CalendarProvider,
)
from capabilities.models.booking import (
    BookingBusinessInfo,
    BookingRequest,
    CalendarBusyInterval,
    PendingArrivalRequest,
    InquiryRequest,
)


class GoogleCalendarProvider(CalendarProvider):

    # Google Calendar event palette: basil, banana and blueberry.
    EVENT_COLORS = {
        "confirmed": "10",
        "pending_arrival": "5",
        "inquiry": "9",
    }

    def __init__(
        self,
        service,
        calendar_id: str = "primary",
        business_info: BookingBusinessInfo | None = None,
    ):
        self.service = service
        self.calendar_id = calendar_id
        self.business_info = business_info

    def get_busy_intervals(
        self,
        start: datetime,
        end: datetime,
    ) -> list[CalendarBusyInterval]:

        response = (
            self.service
            .freebusy()
            .query(
                body={
                    "timeMin": start.isoformat(),
                    "timeMax": end.isoformat(),
                    "items": [
                        {
                            "id": self.calendar_id,
                        }
                    ],
                }
            )
            .execute()
        )

        calendar_data = (
            response
            .get("calendars", {})
            .get(self.calendar_id, {})
        )

        busy_items = calendar_data.get(
            "busy",
            [],
        )

        return [
            CalendarBusyInterval(
                start=self._parse_datetime(
                    item["start"]
                ),
                end=self._parse_datetime(
                    item["end"]
                ),
            )
            for item in busy_items
        ]

    def create_booking_event(
        self,
        request: BookingRequest,
        start: datetime,
        end: datetime,
        service_name: str,
    ) -> str:

        description_lines = [
            "Reserva confirmada",
            "",
            f"Servicio: {service_name}",
        ]

        if self.business_info:

            if self.business_info.name:
                description_lines.append(
                    f"Negocio: {self.business_info.name}"
                )

            if self.business_info.phone:
                description_lines.append(
                    f"Teléfono: {self.business_info.phone}"
                )

            if self.business_info.whatsapp:
                description_lines.append(
                    f"WhatsApp: {self.business_info.whatsapp}"
                )

            if self.business_info.email:
                description_lines.append(
                    f"Email: {self.business_info.email}"
                )

            if self.business_info.address:
                description_lines.append(
                    f"Dirección: {self.business_info.address}"
                )

        if request.notes:
            description_lines.extend(
                [
                    "",
                    f"Notas: {request.notes}",
                ]
            )

        private_properties = {
            "webagent_booking": "true",
            "service_id": request.service_id,
        }

        if request.email:
            private_properties[
                "customer_email"
            ] = request.email

        if request.phone:
            private_properties[
                "customer_phone"
            ] = request.phone

        event = {
            "colorId": self.EVENT_COLORS["confirmed"],
            "summary": (
                f"{request.first_name} "
                f"{request.last_name} "
                f"— {service_name}"
            ),
            "description": "\n".join(
                description_lines
            ),
            "start": {
                "dateTime": start.isoformat(),
            },
            "end": {
                "dateTime": end.isoformat(),
            },
            "extendedProperties": {
                "private": private_properties,
            },
        }

        if (
            self.business_info
            and self.business_info.address
        ):
            event["location"] = (
                self.business_info.address
            )

        if request.email:
            event["attendees"] = [
                {
                    "email": request.email,
                }
            ]

        insert_kwargs = {
            "calendarId": self.calendar_id,
            "body": event,
        }

        if request.email:
            insert_kwargs["sendUpdates"] = "all"

        created_event = (
            self.service
            .events()
            .insert(
                **insert_kwargs
            )
            .execute()
        )

        event_id = created_event.get("id")

        if not event_id:
            raise RuntimeError(
                "Google Calendar no devolvió "
                "un identificador de evento."
            )

        return event_id

    def cancel_event(
        self,
        event_id: str,
    ) -> None:

        (
            self.service
            .events()
            .delete(
                calendarId=self.calendar_id,
                eventId=event_id,
            )
            .execute()
        )

    def create_pending_arrival_event(
        self,
        request: PendingArrivalRequest,
        start: datetime,
        end: datetime,
        option_name: str,
    ) -> str:
        description = [
            "PROPUESTA PENDIENTE: confirma la hora y la capacidad "
            "antes de citar al cliente.",
            f"Motivo: {request.notes}",
            f"Cliente: {request.first_name} {request.last_name}",
        ]
        if request.phone:
            description.append(f"Teléfono del cliente: {request.phone}")
        if request.email:
            description.append(f"Email del cliente: {request.email}")

        event = {
            "colorId": self.EVENT_COLORS["pending_arrival"],
            "summary": (
                f"[PENDIENTE] {option_name} — "
                f"{request.first_name} {request.last_name}"
            ),
            "description": "\n".join(description),
            "start": {"dateTime": start.isoformat()},
            "end": {"dateTime": end.isoformat()},
            "transparency": "transparent",
            "visibility": "private",
            "status": "tentative",
            "extendedProperties": {
                "private": {
                    "webagent_booking": "true",
                    "webagent_status": "pending_arrival",
                    "request_type_id": request.service_id,
                },
            },
        }
        created = (
            self.service.events().insert(
                calendarId=self.calendar_id,
                body=event,
            ).execute()
        )
        event_id = created.get("id")
        if not event_id:
            raise RuntimeError("Google Calendar no devolvió un identificador de evento.")
        return event_id

    def create_inquiry_event(
        self,
        request: InquiryRequest,
        day: date,
        option_name: str,
    ) -> str:
        is_budget = "presupuest" in option_name.casefold()
        description = [
            (
                "PRESUPUESTO PENDIENTE: revisa la solicitud y contacta "
                "con el cliente."
                if is_budget else
                "CONSULTA PENDIENTE: contacta con el cliente para responder."
            ),
            f"Motivo: {request.notes}",
            f"Cliente: {request.first_name} {request.last_name}",
        ]
        if request.phone:
            description.append(f"Teléfono del cliente: {request.phone}")
        if request.email:
            description.append(f"Email del cliente: {request.email}")
        event = {
            "colorId": self.EVENT_COLORS["inquiry"],
            "summary": (
                f"[{'PRESUPUESTO' if is_budget else 'CONSULTA'} PENDIENTE] "
                f"{option_name} — "
                f"{request.first_name} {request.last_name}"
            ),
            "description": "\n".join(description),
            "start": {"date": day.isoformat()},
            "end": {"date": (day + timedelta(days=1)).isoformat()},
            "transparency": "transparent",
            "visibility": "private",
            "status": "tentative",
            "extendedProperties": {
                "private": {
                    "webagent_booking": "true",
                    "webagent_status": "pending_inquiry",
                    "request_type_id": request.service_id,
                },
            },
        }
        created = self.service.events().insert(
            calendarId=self.calendar_id,
            body=event,
        ).execute()
        event_id = created.get("id")
        if not event_id:
            raise RuntimeError("Google Calendar no devolvió un identificador de evento.")
        return event_id

    @staticmethod
    def _parse_datetime(
        value: str,
    ) -> datetime:

        return datetime.fromisoformat(
            value.replace(
                "Z",
                "+00:00",
            )
        )
