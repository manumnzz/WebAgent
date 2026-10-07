from capabilities.capability_inputs import CapabilityInputs
from capabilities.capability_readiness import (
    evaluate_capability_readiness,
)
from capabilities.capability_registry import (
    get_capability_definition,
)


def test_booking_not_ready_without_configuration():
    inputs = CapabilityInputs()

    definition = get_capability_definition("booking")

    readiness = evaluate_capability_readiness(
        definition,
        inputs,
    )

    assert readiness.ready is False
    assert readiness.missing_inputs == [
        "booking_configuration"
    ]


def test_maps_ready_with_business_address():
    inputs = CapabilityInputs(
        business_address="Calle Ejemplo 15, Sevilla"
    )

    definition = get_capability_definition("maps")

    readiness = evaluate_capability_readiness(
        definition,
        inputs,
    )

    assert readiness.ready is True
    assert readiness.missing_inputs == []