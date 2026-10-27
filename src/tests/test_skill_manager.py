import pytest

from agent_skills.manager import SkillManager


def write_skill(root, name, instructions="Instrucciones de prueba."):
    directory = root / name
    directory.mkdir()

    path = directory / "SKILL.md"

    path.write_text(
        f"---\n"
        f"name: {name}\n"
        f"description: Descripción de {name}.\n"
        f"---\n\n"
        f"{instructions}\n",
        encoding="utf-8",
    )

    return path


def test_discovers_metadata_in_stable_order(tmp_path):
    write_skill(tmp_path, "visual-review")
    write_skill(tmp_path, "frontend-design")

    manager = SkillManager(tmp_path)

    catalog = [
        item.model_dump()
        for item in manager.discover()
    ]

    assert [item["name"] for item in catalog] == [
        "frontend-design",
        "visual-review",
    ]

    assert all(
        set(item) == {"name", "description"}
        for item in catalog
    )


def test_loads_only_selected_skills_without_duplicates(tmp_path):
    write_skill(tmp_path, "frontend-design", "DISEÑO")
    write_skill(tmp_path, "visual-review", "REVISIÓN")

    manager = SkillManager(tmp_path)

    context = manager.load([
        "frontend-design",
        "frontend-design",
    ])

    assert context.count("## Skill: frontend-design") == 1
    assert "DISEÑO" in context
    assert "REVISIÓN" not in context


def test_rejects_unknown_skill(tmp_path):
    manager = SkillManager(tmp_path)

    with pytest.raises(ValueError, match="No existe"):
        manager.load(["missing-skill"])


@pytest.mark.parametrize(
    "content",
    [
        "Sin cabecera.",
        "---\nname: frontend-design\n---\nInstrucciones.",
        (
            "---\n"
            "name: other-name\n"
            "description: Descripción.\n"
            "---\nInstrucciones."
        ),
    ],
)
def test_rejects_malformed_skills(tmp_path, content):
    directory = tmp_path / "frontend-design"
    directory.mkdir()

    (directory / "SKILL.md").write_text(
        content,
        encoding="utf-8",
    )

    with pytest.raises(ValueError):
        SkillManager(tmp_path)


def test_rejects_context_over_budget(tmp_path):
    write_skill(tmp_path, "frontend-design", "x" * 100)

    manager = SkillManager(
        tmp_path,
        max_context_chars=50,
    )

    with pytest.raises(ValueError, match="presupuesto"):
        manager.load(["frontend-design"])


def test_rejects_oversized_skill(tmp_path):
    write_skill(tmp_path, "frontend-design", "x" * 100)

    with pytest.raises(ValueError, match="tamaño"):
        SkillManager(
            tmp_path,
            max_skill_bytes=50,
        )


def test_rejects_skill_outside_directory(tmp_path):
    root = tmp_path / "skills"
    root.mkdir()

    outside = tmp_path / "outside"
    outside.mkdir()

    (outside / "SKILL.md").write_text(
        "---\n"
        "name: frontend-design\n"
        "description: Descripción.\n"
        "---\nInstrucciones.",
        encoding="utf-8",
    )

    (root / "frontend-design").symlink_to(
        outside,
        target_is_directory=True,
    )

    with pytest.raises(ValueError, match="directorio permitido"):
        SkillManager(root)