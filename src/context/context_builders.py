from capabilities.capability_registry import get_capability_definition
from capabilities.capability_readiness import evaluate_capability_readiness
from state.project_state import ProjectState
import json

from content.models import WebsiteContent
from content.presentation import CONTENT_CONTRACT
from capabilities.capability_resolver import (
    EDITABLE_CAPABILITIES,
    resolve_ready_capability_implementations,
)

def build_capability_constraints(state: ProjectState) -> list[dict]:
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
        "capability_constraints": build_capability_constraints(state),
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
        "available_media": [
            asset.model_dump(mode="json")
            for asset in state.available_media
        ],
    }

    return json.dumps(context)

def build_developer_context(state: ProjectState) -> str:

    if state.website_spec is None:
        raise ValueError(
            "WebsiteSpec no disponible para DeveloperAgent."
        )

    website_spec_json, implementations_json, instructions = _developer_inputs(state)

    return f"""
        MODE: generate

        WEBSITE_SPEC:
        {website_spec_json}

        PREBUILT_CAPABILITY_IMPLEMENTATIONS:
        {implementations_json}

        {instructions}
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

    website_spec_json, implementations_json, instructions = _developer_inputs(state)
    validation_json = state.validation.model_dump_json(indent=2)

    return f"""
        MODE: repair
        
        WEBSITE_SPEC:
        {website_spec_json}

        PREBUILT_CAPABILITY_IMPLEMENTATIONS:
        {implementations_json}

        {instructions}

        VALIDATION_RESULT:
        {validation_json}
    """


def _developer_inputs(state: ProjectState) -> tuple[str, str, str]:
    spec = state.website_spec
    editable = isinstance(state.website_content, WebsiteContent)
    implementations = resolve_ready_capability_implementations(
        spec, editable_content=editable,
    )

    if editable:
        view = spec.model_dump(mode="json")
        for field in ("contact", "services"):
            view["business"].pop(field, None)
        if any(capability.type == "gallery" for capability in spec.capabilities):
            view["available_media"] = [
                asset for asset in view["available_media"] if asset["role"] != "gallery"
            ]
        for capability in view["capabilities"]:
            if capability["type"] in EDITABLE_CAPABILITIES:
                capability["input_values"] = {}
        website_spec_json = json.dumps(view, indent=2, ensure_ascii=False)
        populated_contact = [
            field for field, value in state.website_content.contact.model_dump().items() if value
        ]
        instructions = (
            CONTENT_CONTRACT + "\nDatos de contacto presentes: "
            + (", ".join(populated_contact) or "ninguno")
        )
    else:
        website_spec_json = spec.model_dump_json(indent=2)
        instructions = ""

    implementations_json = json.dumps(
        [implementation.model_dump() for implementation in implementations],
        indent=2,
    )
    return website_spec_json, implementations_json, instructions
