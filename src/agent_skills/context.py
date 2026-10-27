from collections.abc import Sequence
from pathlib import Path

from agent_skills.manager import SkillManager


SKILLS_DIRECTORY = (
    Path(__file__).resolve().parents[2] / "skills"
)

def build_skill_context(
        *,
        selected_skills: Sequence[str] = ("frontend-design",),
        skills_directory: Path | None = None,
) -> dict:
    manager = SkillManager(
        skills_directory=(
            skills_directory
            if skills_directory is not None
            else SKILLS_DIRECTORY
        ),
    )

    return {
        "catalog": [
            item.model_dump()
            for item in manager.discover()
        ],
        "selected": list(dict.fromkeys(selected_skills)),
        "instructions": manager.load(selected_skills),
    }