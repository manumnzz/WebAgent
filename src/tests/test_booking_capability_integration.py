from unittest.mock import MagicMock

from capabilities.capability_inputs import (
    CapabilityInputs,
)
from capabilities.capability_resolver import (
    resolve_ready_capability_implementations,
)
from capabilities.models.booking import (
    BookingConfiguration,
)
from specs.capability_spec import (
    CapabilityPlan,
    CapabilitySpec,
)
from specs.website_spec_builder import (
    build_website_spec,
)
from agents.business_agent import BusinessProfile
from context.context_builders import (
    build_developer_context,
)


def build_booking_configuration():
    return BookingConfiguration.model_validate(
        {
            "timezone": "Europe/Madrid",
            "services": [
                {
                    "id": "corte",
                    "name": "Corte",
                    "duration_minutes": 30,
                }
            ],
            "weekly_schedule": [
                {
                    "weekday": "monday",
                    "ranges": [
                        {
                            "start": "09:00",
                            "end": "14:00",
                        }
                    ],
                }
            ],
            "slot_interval_minutes": 30,
        }
    )


def test_booking_full_capability_pipeline():

    state = MagicMock()

    # BUSINESS
    state.business = BusinessProfile(
        name="Apex Barber Club",
        business_type="barbería",
        location="Sevilla",
        services=[
            "Corte",
        ],
        main_goal="Permitir reservar citas online.",
        desired_style=[
            "moderno",
        ],
    )

    # UX
    state.ux = MagicMock()
    state.ux.sections = []
    state.ux.navigation = []
    state.ux.primary_cta = "Reservar"
    state.ux.missing_content = []

    # COPY
    state.website_copy = MagicMock()
    state.website_copy.sections = []

    # DESIGN
    state.design = MagicMock()
    state.design.section_designs = []
    state.design.visual_direction = "clean"
    state.design.color_palette = []
    state.design.typography_direction = "modern"
    state.design.missing_information = []
    state.design.missing_assets = []

    # CAPABILITY PLAN
    state.capability_plan = CapabilityPlan(
        capabilities=[
            CapabilitySpec(
                type="booking",
                required=True,
                reason="Permitir reservar citas.",
            )
        ]
    )

    # CAPABILITY INPUTS
    state.capability_inputs = CapabilityInputs(
        booking_configuration=(
            build_booking_configuration()
        )
    )

    website_spec = build_website_spec(
        state
    )

    state.website_spec = website_spec

    booking_spec = next(
        capability
        for capability in website_spec.capabilities
        if capability.type == "booking"
    )

    assert booking_spec.ready is True
    assert booking_spec.missing_inputs == []

    implementations = (
        resolve_ready_capability_implementations(
            website_spec
        )
    )

    booking = next(
        implementation
        for implementation in implementations
        if implementation.type == "booking"
    )

    assert 'href="/reservar"' in booking.html
    developer_context = build_developer_context(
        state
    )

    assert "PREBUILT_CAPABILITY_IMPLEMENTATIONS" in developer_context
    assert '"type": "booking"' in developer_context
    assert 'href=\\"/reservar\\"' in developer_context


def test_pending_only_booking_is_included_even_if_ux_omits_it():
    state = MagicMock()
    state.business = BusinessProfile(
        name="Taller", business_type="taller", location=None,
        services=["Entrega del vehículo"], main_goal=None,
        desired_style=[], requested_features=["booking"],
    )
    state.ux.sections = []
    state.ux.navigation = []
    state.ux.primary_cta = "Proponer entrega"
    state.ux.missing_content = []
    state.website_copy.sections = []
    state.design.section_designs = []
    state.design.visual_direction = "simple"
    state.design.color_palette = []
    state.design.typography_direction = "sans"
    state.design.missing_information = []
    state.design.missing_assets = []
    state.capability_plan = CapabilityPlan(capabilities=[])
    state.capability_inputs = CapabilityInputs(
        booking_configuration=BookingConfiguration.model_validate({
            "timezone": "Europe/Madrid",
            "services": [],
            "pending_arrival_types": [
                {"id": "car-dropoff", "name": "Entrega del vehículo"}
            ],
            "weekly_schedule": [
                {"weekday": "monday", "ranges": [
                    {"start": "09:00", "end": "14:00"}
                ]}
            ],
        })
    )

    spec = build_website_spec(state)

    assert [capability.type for capability in spec.capabilities] == ["booking"]
    assert spec.capabilities[0].ready is True
    assert 'href="/reservar"' in (
        resolve_ready_capability_implementations(spec)[0].html
    )
