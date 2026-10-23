from html import escape
from urllib.parse import quote

from capabilities.capability_implementation import (
    CapabilityImplementation,
)

from capabilities.models.booking import (
    BookingConfiguration,
)

def build_booking_implementation(
        booking_configuration: BookingConfiguration | dict,
) -> CapabilityImplementation:

    configuration = BookingConfiguration.model_validate(
        booking_configuration
    )

    if not (
        configuration.services or configuration.pending_arrival_types
        or configuration.inquiry_types
    ):
        raise ValueError(
            "Booking necesita al menos una opción de cita."
        )

    html = """
<a
    class="capability-booking"
    href="/reservar"
>
    Ver citas y solicitudes
</a>
""".strip()

    for inquiry in configuration.inquiry_types:
        href = f"/reservar?service_id={quote(inquiry.id, safe='')}"
        html += (
            f'\n<a class="capability-booking capability-booking-inquiry" '
            f'href="{href}">{escape(inquiry.name)}</a>'
        )

    return CapabilityImplementation(
        type="booking",
        html=html,
        css="",
        javascript="",
        implementation_notes=[
            (
                "La reserva se realiza mediante la ruta /reservar. "
                "Las llegadas sin duración son solicitudes pendientes de "
                "confirmación por el negocio. No implementar lógica de calendario "
                "en el frontend principal."
            ),
            (
                "La llamada a la acción puede adaptarse visualmente "
                "al diseño de la web, pero debe conservar href=\"/reservar\"."
            ),
            (
                "Cada enlace de consulta sin hora apunta a su opción concreta "
                "de /reservar. Si una opción es Solicitar presupuesto, los "
                "botones de presupuesto deben usar ese enlace; no crear un "
                "formulario mailto: para la misma solicitud."
            ),
        ],
    )
