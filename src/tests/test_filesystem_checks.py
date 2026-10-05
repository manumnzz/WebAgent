from validation.checks.filesystem_checks import validate_filesystem

def test_valid_filesystem(tmp_path):
    (tmp_path / "index.html").write_text(
        "<html></html>",
        encoding="utf-8"
    )

    (tmp_path / "styles.css").write_text(
        "body {}",
        encoding="utf-8"
    )

    (tmp_path / "script.js").write_text(
        "console.log('WebAgent');",
        encoding="utf-8"
    )

    errors = validate_filesystem(tmp_path)

    assert errors == []

def test_missing_file(tmp_path):
    (tmp_path / "index.html").write_text(
        "<html></html>",
        encoding="utf-8"
    )

    (tmp_path / "styles.css").write_text(
        "body {}",
        encoding="utf-8"
    )

    errors = validate_filesystem(tmp_path)

    assert any(
        error.code == "missing_file"
        and error.file == "script.js"
        for error in errors
    )

def test_empty_file(tmp_path):
    (tmp_path / "index.html").write_text(
        "<html></html>",
        encoding="utf-8"
    )

    (tmp_path / "styles.css").write_text(
        "body {}",
        encoding="utf-8"
    )

    (tmp_path / "script.js").write_text(
        "",
        encoding="utf-8"
    )

    errors = validate_filesystem(tmp_path)

    assert any(
        error.code == "empty_file"
        and error.file == "script.js"
        for error in errors
    )

def test_whitespace_only_file_is_empty(tmp_path):
    (tmp_path / "index.html").write_text(
        "<html></html>",
        encoding="utf-8"
    )

    (tmp_path / "styles.css").write_text(
        "body {}",
        encoding="utf-8"
    )

    (tmp_path / "script.js").write_text(
        "   \n   \n   ",
        encoding="utf-8"
    )

    errors = validate_filesystem(tmp_path)

    assert any(
        error.code == "empty_file"
        and error.file == "script.js"
        for error in errors
    )

