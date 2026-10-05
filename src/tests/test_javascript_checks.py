from validation.checks.javascript_checks import validate_javascript


def test_valid_javascript():
    content = """
    function greet(name) {
        const message = "Hola " + name;
        console.log(message);
    }
    
    greet("Manuel");
    """

    errors = validate_javascript(content)

    assert errors == []

def test_unclosed_js_delimiter():
    content = """
    function greet(name) {
        console.log(name);
    """

    errors = validate_javascript(content)

    assert any(
        error.code == "unclosed_js_delimiter"
        for error in errors
    )

def test_unexpected_js_closing_delimiter():
    content = """
    function greet(name) {
        console.log(name);
    ]
    """

    errors = validate_javascript(content)

    assert any(
        error.code == "unexpected_js_closing_delimiter"
        for error in errors
    )

def test_unclosed_js_block_comment():
    content = """
    function greet(name) {
        /* Este comentario nunca termina
        console.log(name);
    }
    """

    errors = validate_javascript(content)

    assert any(
        error.code == "unclosed_js_block_comment"
        for error in errors
    )

def test_unclosed_js_string():
    content = """
    const message = "Hola Manuel;
    """

    errors = validate_javascript(content)

    assert any(
        error.code == "unclosed_js_string"
        for error in errors
    )

def test_unclosed_js_template_literal():
    content = """
    const message = `Hola Manuel;
    """

    errors = validate_javascript(content)

    assert any(
        error.code == "unclosed_js_template_literal"
        for error in errors
    )