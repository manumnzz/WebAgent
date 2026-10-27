from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict, Field


class SkillMetadata(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: str = Field(
        min_length=1,
        max_length=64,
        pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
    )

    description: str = Field(
        min_length=1,
        max_length=600,
    )


@dataclass(frozen=True)
class LoadedSkill:
    metadata: SkillMetadata
    instructions: str


class SkillManager:
    def __init__(
        self,
        skills_directory: Path,
        *,
        max_skill_bytes: int = 32_768,
        max_context_chars: int = 24_000,
    ):
        if max_skill_bytes < 1 or max_context_chars < 1:
            raise ValueError("Los límites deben ser positivos.")

        self.directory = skills_directory.resolve()
        self.max_skill_bytes = max_skill_bytes
        self.max_context_chars = max_context_chars

        if not self.directory.is_dir():
            raise FileNotFoundError(
                f"No existe el directorio de skills: "
                f"{self.directory}"
            )

        self._skills: dict[str, LoadedSkill] = {}

        for path in sorted(self.directory.glob("*/SKILL.md")):
            skill = self._read_skill(path)
            name = skill.metadata.name

            if name in self._skills:
                raise ValueError(
                    f"Skill duplicada: '{name}'."
                )

            self._skills[name] = skill

    def _read_skill(self, path: Path) -> LoadedSkill:
        resolved_path = path.resolve()

        if not resolved_path.is_relative_to(self.directory):
            raise ValueError(
                f"La skill sale del directorio permitido: {path}"
            )

        with resolved_path.open("rb") as source:
            content = source.read(self.max_skill_bytes + 1)

        if len(content) > self.max_skill_bytes:
            raise ValueError(
                f"La skill supera el límite de tamaño: {path}"
            )

        lines = content.decode("utf-8").splitlines()

        if not lines or lines[0] != "---":
            raise ValueError(
                f"Falta la cabecera YAML en {path}."
            )

        try:
            closing_index = lines.index("---", 1)
        except ValueError as error:
            raise ValueError(
                f"La cabecera YAML no está cerrada en {path}."
            ) from error

        try:
            header = yaml.safe_load(
                "\n".join(lines[1:closing_index])
            )
        except yaml.YAMLError as error:
            raise ValueError(
                f"Cabecera YAML inválida en {path}."
            ) from error

        if not isinstance(header, dict):
            raise ValueError(
                f"La cabecera debe contener campos en {path}."
            )

        metadata = SkillMetadata.model_validate(header)

        if metadata.name != path.parent.name:
            raise ValueError(
                "El nombre de la skill debe coincidir "
                f"con su carpeta: {path}."
            )

        instructions = "\n".join(
            lines[closing_index + 1:]
        ).strip()

        if not instructions:
            raise ValueError(
                f"La skill no contiene instrucciones: {path}."
            )

        return LoadedSkill(
            metadata=metadata,
            instructions=instructions,
        )

    def discover(self) -> list[SkillMetadata]:
        return [
            self._skills[name].metadata
            for name in sorted(self._skills)
        ]

    def load(self, names: Sequence[str]) -> str:
        sections = []

        for name in dict.fromkeys(names):
            if name not in self._skills:
                raise ValueError(
                    f"No existe la skill '{name}'."
                )

            skill = self._skills[name]

            sections.append(
                f"## Skill: {name}\n\n"
                f"{skill.instructions}"
            )

        context = "\n\n".join(sections)

        if len(context) > self.max_context_chars:
            raise ValueError(
                "Las skills seleccionadas superan "
                "el presupuesto de contexto."
            )

        return context