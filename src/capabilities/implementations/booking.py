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

    if not configuration.services:
        raise ValueError(
            "Booking necesita al menos un servicio."
        )

    html = """
<a
    class="capability-booking"
    href="/reservar"
>
    Reservar cita
</a>
""".strip()

    return CapabilityImplementation(
        type="booking",
        html=html,
        css="",
        javascript="",
        implementation_notes=[
            (
                "La reserva se realiza mediante la ruta /reservar. "
                "No implementar lógica de disponibilidad o calendario "
                "en el frontend principal."
            ),
            (
                "La llamada a la acción puede adaptarse visualmente "
                "al diseño de la web, pero debe conservar href=\"/reservar\"."
            ),
        ],
    )