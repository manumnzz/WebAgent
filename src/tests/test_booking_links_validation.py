from capabilities.models.booking import BookingConfiguration, InquiryType
from validation.checks.booking_links import validate_booking_inquiry_links


def test_budget_cta_must_open_its_configured_calendar_inquiry():
    configuration = BookingConfiguration(
        timezone="Europe/Madrid",
        inquiry_types=[
            InquiryType(
                id="solicitar-presupuesto",
                name="Solicitar presupuesto",
            )
        ],
    )

    wrong = '<a href="mailto:shop@example.com">Solicitar presupuesto</a>'
    correct = (
        '<a href="/reservar?service_id=solicitar-presupuesto">Solicitar presupuesto</a>'
    )

    assert validate_booking_inquiry_links(wrong, configuration)[0].code == (
        "invalid_budget_link"
    )
    assert validate_booking_inquiry_links(correct, configuration) == []
    assert validate_booking_inquiry_links(correct + wrong, configuration)


def inquiry_configuration():
    return BookingConfiguration(
        timezone="Europe/Madrid",
        inquiry_types=[InquiryType(id="presupuesto", name="Presupuesto")],
    )


def test_internal_navigation_reaches_single_real_action():
    html = '<nav><a href="#consulta">Presupuesto</a></nav><section id="consulta"><a id="accion" href="/reservar?service_id=presupuesto">Solicitar presupuesto</a></section><a href="#accion">Pedir presupuesto</a>'
    assert validate_booking_inquiry_links(html, inquiry_configuration()) == []


def test_internal_navigation_does_not_hide_wrong_destination():
    html = '<a href="#consulta">Presupuesto</a><section id="consulta"><a href="mailto:shop@example.com">Enviar</a></section>'
    assert validate_booking_inquiry_links(html, inquiry_configuration())


def test_missing_fragment_and_cycles_do_not_pass():
    for html in [
        '<a href="#ausente">Presupuesto</a>',
        '<a id="uno" href="#dos">Presupuesto</a><a id="dos" href="#uno">Volver</a>',
    ]:
        assert validate_booking_inquiry_links(html, inquiry_configuration())


def test_external_lookalike_and_ambiguous_service_id_are_rejected():
    for href in [
        "https://example.com/reservar?service_id=presupuesto",
        "//example.com/reservar?service_id=presupuesto",
        "/reservar?service_id=presupuesto&service_id=other",
        "/reservar?service_id=",
        "/reservar?service_id=other",
    ]:
        assert validate_booking_inquiry_links(
            f'<a href="{href}">Presupuesto</a>', inquiry_configuration()
        )


def test_target_must_contain_the_action_not_a_sibling():
    html = '<a href="#vacio">Presupuesto</a><section id="vacio"></section><a href="/reservar?service_id=presupuesto">Solicitar presupuesto</a>'
    assert validate_booking_inquiry_links(html, inquiry_configuration())
