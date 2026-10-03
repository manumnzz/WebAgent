from validation.checks.css_checks import validate_css


def test_valid_css():

    css = """
    .hero {
        color: white;
        padding: 20px;
    }
    """

    errors = validate_css(css)

    assert errors == []


def test_unclosed_css_block():

    css = """
    .hero {
        color: white;
    """

    errors = validate_css(css)

    assert len(errors) == 1
    assert errors[0].code == "unclosed_css_block"


def test_unclosed_css_comment():

    css = """
    .hero {
        color: white;
    }

    /* comentario sin cerrar
    """

    errors = validate_css(css)

    assert len(errors) == 1
    assert errors[0].code == "unclosed_css_comment"

def test_unclosed_css_string():

    css = """
    .hero::after {
        content: "Hola;
    }
    """

    errors = validate_css(css)

    assert any(
        error.code == "unclosed_css_string"
        for error in errors
    )
