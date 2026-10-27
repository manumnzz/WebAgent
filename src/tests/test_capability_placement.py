import pytest

from capabilities.placement_policy import (
    CapabilityPlacementPolicy,
)
from specs.website_spec import WebsiteCapabilitySpec
from validation.checks.capability_placement import (
    validate_capability_placement,
)
from validation.validator import validate_website


def build_capability(capability_type, maximum):
    return WebsiteCapabilitySpec(
        type=capability_type,
        required=True,
        reason="Prueba de límites.",
        description="Capability de prueba.",
        required_inputs=[],
        ready=True,
        missing_inputs=[],
        input_values={},
        developer_requirements=[],
        placement_policy=CapabilityPlacementPolicy(
            max_instances=maximum,
        ),
    )


@pytest.mark.parametrize(
    ("content", "capability_type", "maximum", "expected_errors"),
    [
        # Dos enlaces de WhatsApp están permitidos.
        (
            '<a href="https://wa.me/34612345678">WhatsApp</a>'
            '<a href="https://wa.me/34612345678">Contactar</a>',
            "whatsapp",
            2,
            0,
        ),
        # El tercero supera el límite aunque no tenga clase.
        (
            '<a href="https://wa.me/34612345678">WhatsApp</a>'
            '<a href="https://wa.me/34612345678">Contactar</a>'
            '<a href="https://wa.me/34612345678">Escribir</a>',
            "whatsapp",
            2,
            1,
        ),
        # Clase y URL identifican el mismo enlace.
        (
            '<a class="capability-whatsapp" '
            'href="https://wa.me/34612345678">WhatsApp</a>',
            "whatsapp",
            1,
            0,
        ),
        # Fotografías y navegación no duplican una galería.
        (
            '<a href="#galeria">Galería</a>'
            '<div id="galeria" class="capability-gallery">'
            '<figure class="capability-gallery-item"></figure>'
            '<figure class="capability-gallery-item"></figure>'
            '</div>',
            "gallery",
            1,
            0,
        ),
        # Dos contenedores sí son dos galerías.
        (
            '<div class="capability-gallery"></div>'
            '<div class="capability-gallery"></div>',
            "gallery",
            1,
            1,
        ),
        # Una consulta concreta no duplica el acceso general.
        (
            '<a href="/reservar">Reservar</a>'
            '<a href="/reservar?service_id=presupuesto">'
            'Pedir presupuesto</a>',
            "booking",
            1,
            0,
        ),
        # Dos accesos generales superan el límite de uno.
        (
            '<a href="/reservar">Reservar</a>'
            '<a href="/reservar">Ver citas</a>',
            "booking",
            1,
            1,
        ),
    ],
)
def test_capability_instance_limits(
    content,
    capability_type,
    maximum,
    expected_errors,
):
    capability = build_capability(
        capability_type,
        maximum,
    )

    errors = validate_capability_placement(
        content,
        [capability],
    )

    assert len(errors) == expected_errors

    if expected_errors:
        assert errors[0].code == (
            "capability_instance_limit_exceeded"
        )
        assert errors[0].file == "index.html"

@pytest.mark.parametrize(
    ("whatsapp_count", "duplicate_ids", "expected_codes"),
    [
        (2, False, set()),
        (
            3,
            False,
            {"capability_instance_limit_exceeded"},
        ),
        (
            2,
            True,
            {"duplicate_html_id"},
        ),
        (
            3,
            True,
            {
                "capability_instance_limit_exceeded",
                "duplicate_html_id",
            },
        ),
    ],
)
def test_website_validator_combines_html_and_capability_checks(
    tmp_path,
    whatsapp_count,
    duplicate_ids,
    expected_codes,
):
    whatsapp_links = (
        '<a href="https://wa.me/34612345678">'
        'WhatsApp</a>'
    ) * whatsapp_count

    extra_html = (
        '<div id="contacto"></div>'
        '<div id="contacto"></div>'
        if duplicate_ids
        else ""
    )

    html = f"""
<!doctype html>
<html lang="es">
<head>
    <meta charset="utf-8">
    <title>Negocio de prueba</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    {whatsapp_links}
    {extra_html}
    <script src="script.js"></script>
</body>
</html>
"""

    (tmp_path / "index.html").write_text(
        html,
        encoding="utf-8",
    )

    (tmp_path / "styles.css").write_text(
        "body { margin: 0; }",
        encoding="utf-8",
    )

    (tmp_path / "script.js").write_text(
        '"use strict";',
        encoding="utf-8",
    )

    result = validate_website(
        website_root=tmp_path,
        capabilities=[
            build_capability("whatsapp", 2),
        ],
    )

    actual_codes = {
        issue.code
        for issue in result.errors
    }

    assert actual_codes == expected_codes
    assert result.is_valid == (not expected_codes)


@pytest.mark.parametrize(
    ("content", "expected_codes"),
    [
        # Hereda la zona a través de contenedores intermedios.
        (
            '<section data-capability-zone="contact">'
            '<div><a href="https://wa.me/34612345678">'
            'WhatsApp</a></div>'
            '</section>',
            set(),
        ),
        # La zona existe, pero no está permitida.
        (
            '<footer data-capability-zone="footer">'
            '<a href="https://wa.me/34612345678">'
            'WhatsApp</a>'
            '</footer>',
            {"invalid_capability_zone"},
        ),
        # No hay ninguna zona declarada.
        (
            '<a href="https://wa.me/34612345678">'
            'WhatsApp</a>',
            {"missing_capability_zone"},
        ),
        # La zona del propio elemento tiene prioridad.
        (
            '<footer data-capability-zone="footer">'
            '<a data-capability-zone="floating" '
            'href="https://wa.me/34612345678">'
            'WhatsApp</a>'
            '</footer>',
            set(),
        ),
        # Una zona cerrada no afecta al siguiente enlace.
        (
            '<section data-capability-zone="contact">'
            '</section>'
            '<a href="https://wa.me/34612345678">'
            'WhatsApp</a>',
            {"missing_capability_zone"},
        ),
        # Una imagen no deja una zona abierta.
        (
            '<section data-capability-zone="contact">'
            '<img data-capability-zone="footer" src="foto.webp">'
            '<a href="https://wa.me/34612345678">'
            'WhatsApp</a>'
            '</section>',
            set(),
        ),
        # Una zona vacía es inválida.
        (
            '<a data-capability-zone="" '
            'href="https://wa.me/34612345678">'
            'WhatsApp</a>',
            {"invalid_capability_zone"},
        ),
        # Al cerrar una zona interna se recupera la exterior.
        (
            '<section data-capability-zone="contact">'
            '<div data-capability-zone="footer"></div>'
            '<a href="https://wa.me/34612345678">'
            'WhatsApp</a>'
            '</section>',
            set(),
        ),
    ],
)
def test_capability_zones(content, expected_codes):
    capability = build_capability("whatsapp", 2)

    capability.placement_policy = CapabilityPlacementPolicy(
        max_instances=2,
        allowed_zones=("contact", "floating"),
    )

    errors = validate_capability_placement(
        content,
        [capability],
    )

    assert {
        issue.code
        for issue in errors
    } == expected_codes


@pytest.mark.parametrize(
    ("links", "zone", "expected_codes"),
    [
        (
            [
                "/reservar",
                "/reservar?service_id=presupuesto",
                "/reservar?service_id=diagnostico",
            ],
            "contact",
            set(),
        ),
        (
            [
                "/reservar?service_id=presupuesto",
                "/reservar?service_id=presupuesto",
            ],
            "contact",
            {"capability_instance_limit_exceeded"},
        ),
        (
            [
                "/reservar?service_id=presupuesto",
                "/reservar?service_id=%70resupuesto",
            ],
            "contact",
            {"capability_instance_limit_exceeded"},
        ),
        (
            ["/reservar?service_id="],
            "contact",
            {"invalid_booking_target"},
        ),
        (
            [
                "/reservar?service_id=presupuesto"
                "&amp;service_id=diagnostico",
            ],
            "contact",
            {"invalid_booking_target"},
        ),
        (
            ["/reservar?service_id=presupuesto"],
            "floating",
            {"invalid_capability_zone"},
        ),
        (
            ["/reservar?service_id=presupuesto"],
            "content",
            set(),
        ),
    ],
)
def test_booking_option_placement(
    links,
    zone,
    expected_codes,
):
    capability = build_capability("booking", 1)

    capability.placement_policy = CapabilityPlacementPolicy(
        max_instances=1,
        allowed_zones=("contact", "content"),
    )

    anchors = "".join(
        f'<a href="{href}">Ver opción</a>'
        for href in links
    )

    content = (
        f'<section data-capability-zone="{zone}">'
        f"{anchors}"
        "</section>"
    )

    errors = validate_capability_placement(
        content,
        [capability],
    )

    assert {
        issue.code
        for issue in errors
    } == expected_codes