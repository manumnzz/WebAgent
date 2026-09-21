from state.project_state import ProjectState

from specs.website_spec import (
    WebsiteSpec,
    WebsiteSectionSpec
)

def build_website_spec(state: ProjectState) -> WebsiteSpec:

    if state.business is None:
        raise ValueError(
            "No se puede construir WebsiteSpec: falta state.business."
        )

    if state.ux is None:
        raise ValueError(
            "No se puede construir WebsiteSpec: falta state.ux."
        )

    if state.website_copy is None:
        raise ValueError(
            "No se puede construir WebsiteSpec: falta state.website_copy."
        )

    if state.design is None:
        raise ValueError(
            "No se puede construir WebsiteSpec: falta state.design."
        )

    copy_by_section = {
        section.section_name: section
        for section in state.website_copy.sections
    }

    design_by_section = {
        section.section_name: section
        for section in state.design.section_designs
    }   

    sections = []

    for ux_section in state.ux.sections:

        copy_section = copy_by_section.get(
            ux_section.name
        )

        design_section = design_by_section.get(
            ux_section.name
        )

        if copy_section is None:
            raise ValueError(
                f"No existe copy para la sección '{ux_section.name}'."
            )

        if design_section is None:
            raise ValueError(
                f"No existe diseño para la sección '{ux_section.name}'."
            )

        section_spec = WebsiteSectionSpec(
            name=ux_section.name,
            purpose=ux_section.purpose,

            # COPY
            headline=copy_section.headline,
            body=copy_section.body,
            cta=copy_section.cta,
            copy_ready=copy_section.ready,
            missing_copy_requirements=copy_section.missing_requirements,

            # DESIGN
            layout=design_section.layout,
            visual_notes=design_section.visual_notes,
            required_inputs=design_section.required_inputs
        )

        sections.append(section_spec)

    return WebsiteSpec(
        business=state.business,

        navigation=state.ux.navigation,
        primary_cta=state.ux.primary_cta,

        visual_direction=state.design.visual_direction,
        color_palette=state.design.color_palette,
        typography_direction=state.design.typography_direction,

        sections=sections,

        missing_content=state.ux.missing_content,
        missing_information=state.design.missing_information,
        missing_assets=state.design.missing_assets
    )