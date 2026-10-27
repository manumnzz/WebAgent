from state.project_state import ProjectState

import json

from capabilities.capability_resolver import (
    resolve_ready_capability_implementations,
)

from agent_skills.context import build_skill_context
from capabilities.capability_registry import get_capability_definition
from capabilities.capability_readiness import evaluate_capability_readiness


def design_capability_constraints(state: ProjectState) -> list[dict]:
    if state.website_spec is not None:
        return [{"type": c.type, "ready": c.ready,
                 "placement_policy": c.placement_policy.model_dump(),
                 "missing_inputs": c.missing_inputs}
                for c in state.website_spec.capabilities]
    constraints = []
    if state.capability_plan is not None:
        for capability in state.capability_plan.capabilities:
            definition = get_capability_definition(capability.type)
            readiness = evaluate_capability_readiness(definition, state.capability_inputs)
            constraints.append({"type": capability.type, "ready": readiness.ready,
                "placement_policy": definition.placement_policy.model_dump(),
                "missing_inputs": readiness.missing_inputs})
    return constraints


def build_ux_context(state: ProjectState) -> str:

    if state.business is None:
        raise ValueError(
            "No se puede construir el contexto del UXAgent "
            "porque state.business todavía no existe."
        )
    return state.business.model_dump_json()

def build_copy_context(state: ProjectState) -> str:

    if state.business is None:
        raise ValueError(
            "No se puede construir el contexto del CopyAgent "
            "porque state.business todavía no existe."
        )

    if state.ux is None:
        raise ValueError(
            "No se puede construir el contexto del CopyAgent "
            "porque state.ux todavía no existe."
        )

    context = {
        "business": state.business.model_dump(),
        "ux": state.ux.model_dump(),
        "available_media": [asset.model_dump(mode="json") for asset in state.available_media],
        "capability_constraints": design_capability_constraints(state),
    }

    return json.dumps(context)

def build_design_context(state: ProjectState) -> str:

    if state.business is None:
        raise ValueError(
            "No se puede construir el modelo del DesignAgent "
            "porque state.business todavía no existe."
        )

    if state.ux is None:
        raise ValueError(
            "No se puede construir el contexto del DesignAgent "
            "porque state.ux todavía no existe."
        )

    context = {
        "business": state.business.model_dump(),
        "ux": state.ux.model_dump(),
        "capability_constraints": design_capability_constraints(state),
        "website_copy": (
            state.website_copy.model_dump()
            if state.website_copy is not None else None
        ),
        "available_media": [
            asset.model_dump(mode="json")
            for asset in state.available_media
        ],
        "skills": build_skill_context(),
    }

    return json.dumps(context)

def build_developer_context(state: ProjectState) -> str:

    if state.website_spec is None:
        raise ValueError(
            "WebsiteSpec no disponible para DeveloperAgent."
        )

    website_spec_json = state.website_spec.model_dump_json(indent=2)

    implementations = (
        resolve_ready_capability_implementations(
            state.website_spec
        )
    )

    implementations_json = json.dumps(
        [
            implementation.model_dump()
            for implementation in implementations
        ],
        indent=2,
    )

    skills_json = json.dumps(
        build_skill_context(),
        ensure_ascii=False,
        indent=2,
    )

    return f"""
        MODE: generate

        WEBSITE_SPEC:
        {website_spec_json}

        PREBUILT_CAPABILITY_IMPLEMENTATIONS:
        {implementations_json}

        SKILLS:
        {skills_json}
    """

def build_developer_repair_context(state: ProjectState) -> str:

    if state.website_spec is None:
        raise ValueError(
            "WebsiteSpec no disponible para DeveloperAgent."
        )

    if state.validation is None:
        raise ValueError(
            "ValidationResult no disponible para reparación."
        )

    website_spec_json = state.website_spec.model_dump_json(indent=2)

    validation_json = state.validation.model_dump_json(indent=2)

    implementations = (
        resolve_ready_capability_implementations(
            state.website_spec
        )
    )

    implementations_json = json.dumps(
        [
            implementation.model_dump()
            for implementation in implementations
        ],
        indent=2,
    )

    skills_json = json.dumps(
            build_skill_context(),
            ensure_ascii=False,
            indent=2,
    )

    return f"""
        MODE: repair
        
        WEBSITE_SPEC:
        {website_spec_json}

        PREBUILT_CAPABILITY_IMPLEMENTATIONS:
        {implementations_json}

        SKILLS:
        {skills_json}

        VALIDATION_RESULT:
        {validation_json}
    """
