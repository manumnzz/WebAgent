from capabilities.models.booking import BookingConfiguration, InquiryType
from validation.checks.booking_links import validate_booking_inquiry_links


def test_budget_cta_must_open_its_configured_calendar_inquiry():
    configuration = BookingConfiguration(
        timezone="Europe/Madrid",
        inquiry_types=[InquiryType(
            id="solicitar-presupuesto", name="Solicitar presupuesto",
        )],
    )

    wrong = '<a href="mailto:shop@example.com">Solicitar presupuesto</a>'
    correct = (
        '<a href="/reservar?service_id=solicitar-presupuesto">'
        'Solicitar presupuesto</a>'
    )

    assert validate_booking_inquiry_links(wrong, configuration)[0].code == (
        "invalid_budget_link"
    )
    assert validate_booking_inquiry_links(correct, configuration) == []
    assert validate_booking_inquiry_links(correct + wrong, configuration)
