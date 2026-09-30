from state.project_state import ProjectState
import json

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
        "ux": state.ux.model_dump()
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
        "ux": state.ux.model_dump()
    }

    return json.dumps(context)

def build_developer_context(state: ProjectState) -> str:

    if state.website_spec is None:
        raise ValueError(
            "WebsiteSpec no disponible para DeveloperAgent."
        )

    website_spec_json = state.website_spec.model_dump_json(indent=2)

    return f"""
        MODE: generate

        WEBSITE_SPEC:
        {website_spec_json}
    """
