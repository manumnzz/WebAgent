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
        ],
    )
