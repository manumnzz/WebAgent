from validation.checks.html_checks import validate_html


def test_valid_html():
    content = """
    <!DOCTYPE html>
    <html>
    <head>
        <link rel="stylesheet" href="styles.css">
    </head>
    <body>
        <section id="inicio">
            <h1>WebAgent</h1>
            <a href="#contacto">Contacto</a>
        </section>

        <section id="contacto">
            <p>Contacta con nosotros</p>
        </section>

        <script src="script.js"></script>
    </body>
    </html>
    """

    errors = validate_html(content)

    assert errors == []

def test_missing_html_tag():
    content = """
    <head>
        <link rel="stylesheet" href="styles.css">
    </head>
    <body>
        <script src="script.js"></script>
    </body>
    """

    errors = validate_html(content)

    assert any(
        error.code == "missing_html_tag"
        for error in errors
    )

def test_missing_html_closing_tag():
    content = """
    <html>
    <head>
        <link rel="stylesheet" href="styles.css">
    </head>
    <body>
        <script src="script.js"></script>
    </body>
    """

    errors = validate_html(content)

    assert any(
        error.code == "missing_html_closing_tag"
        for error in errors
    )

def test_missing_head_tag():
    content = """
    <html>
    <body>
        <script src="script.js"></script>
    </body>
    </html>
    """

    errors = validate_html(content)

    assert any(
        error.code == "missing_head_tag"
        for error in errors
    )

def test_missing_body_tag():
    content = """
    <html>
    <head>
        <link rel="stylesheet" href="styles.css">
    </head>
    </html>
    """

    errors = validate_html(content)

    assert any(
        error.code == "missing_body_tag"
        for error in errors
    )

def test_missing_stylesheet_reference():
    content = """
    <html>
    <head>
    </head>
    <body>
        <script src="script.js"></script>
    </body>
    </html>
    """

    errors = validate_html(content)

    assert any(
        error.code == "missing_stylesheet_reference"
        for error in errors
    )

def test_missing_script_reference():
    content = """
    <html>
    <head>
        <link rel="stylesheet" href="styles.css">
    </head>
    <body>
    </body>
    </html>
    """

    errors = validate_html(content)

    assert any(
        error.code == "missing_script_reference"
        for error in errors
    )

def test_duplicate_html_id():
    content = """
    <html>
    <head>
        <link rel="stylesheet" href="styles.css">
    </head>
    <body>

        <section id="servicios">
            <h2>Servicios</h2>
        </section>

        <section id="servicios">
            <h2>Otros servicios</h2>
        </section>

        <script src="script.js"></script>
    </body>
    </html>
    """

    errors = validate_html(content)

    assert any(
        error.code == "duplicate_html_id"
        for error in errors
    )

def test_broken_internal_link():
    content = """
    <html>
    <head>
        <link rel="stylesheet" href="styles.css">
    </head>
    <body>

        <a href="#reservar">Reservar cita</a>

        <section id="reservas">
            <h2>Reservas</h2>
        </section>

        <script src="script.js"></script>
    </body>
    </html>
    """

    errors = validate_html(content)

    assert any(
        error.code == "broken_internal_link"
        for error in errors
    )

