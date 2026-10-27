import pytest

from validation.checks.public_content import (
    validate_public_content,
)
from validation.validator import validate_website


@pytest.mark.parametrize(
    "text",
    [
        "Información pendiente de completar.",
        "Contexto visual pendiente de confirmar.",
        "El negocio aún debe confirmar las marcas.",
        "Estarán disponibles cuando el negocio facilite textos reales.",
        "Horario e indicaciones adicionales pendientes de confirmación.",
        "Opiniones verificadas pendientes de incorporar.",
    ],
)
def test_detects_internal_notes(text):
    errors = validate_public_content(f"<p>{text}</p>")

    assert errors
    assert all(
        issue.code == "public_internal_note"
        for issue in errors
    )


def test_detects_notes_split_across_elements():
    errors = validate_public_content(
        "<p>Información <strong>pendiente</strong> "
        "de completar.</p>"
    )

    assert errors[0].code == "public_internal_note"


@pytest.mark.parametrize(
    "text",
    [
        "Tu solicitud está pendiente de confirmación.",
        "Próximamente abriremos una nueva sede.",
        "Consulta el estado de tu presupuesto pendiente.",
    ],
)
def test_allows_legitimate_public_messages(text):
    assert validate_public_content(f"<p>{text}</p>") == []


def test_ignores_comments_scripts_styles_and_templates():
    content = """
    <!-- Información pendiente de completar. -->
    <script>
        const message = "Información pendiente de completar.";
    </script>
    <style>
        /* Información pendiente de completar. */
    </style>
    <template>
        Información pendiente de completar.
    </template>
    <p>Contacta con nuestro taller.</p>
    """

    assert validate_public_content(content) == []


def test_checks_public_attributes():
    errors = validate_public_content(
        '<img src="foto.webp" '
        'alt="Contexto visual pendiente de confirmar.">'
    )

    assert errors[0].code == "public_internal_note"


@pytest.mark.parametrize(
    ("body", "expected_valid"),
    [
        ("<p>Contacta con el taller.</p>", True),
        ("<p>Información pendiente de completar.</p>", False),
    ],
)
def test_website_validator_checks_public_content(
    tmp_path,
    body,
    expected_valid,
):
    (tmp_path / "index.html").write_text(
        '<html><head>'
        '<link rel="stylesheet" href="styles.css">'
        '</head><body>'
        f'{body}'
        '<script src="script.js"></script>'
        '</body></html>',
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

    result = validate_website(website_root=tmp_path)

    assert result.is_valid is expected_valid

    if not expected_valid:
        assert any(
            issue.code == "public_internal_note"
            for issue in result.errors
        )