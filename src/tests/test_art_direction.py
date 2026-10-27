import json
from agents.business_agent import BusinessProfile
from agents.copy_agent import WebsiteCopy, SectionCopy
from agents.design_agent import DesignSpec, SectionDesign
from agents.ux_agent import WebsiteStructure, SectionSpec
from context.context_builders import build_design_context
from specs.art_direction import ArtDirection, SectionComposition
from specs.capability_spec import CapabilityPlan
from specs.website_spec_builder import build_website_spec
from state.project_state import ProjectState


def test_real_copy_and_composition_survive_pipeline():
    composition = SectionComposition(
        desktop="Texto 5fr, imagen 7fr",
        mobile="Texto, CTA, imagen",
        focal_point="Titular",
        content_width="62ch",
        surface="Blanca",
        asset_paths=[],
        image_fit="contain",
    )
    state = ProjectState(
        business=BusinessProfile(
            name="Prueba",
            business_type="taller",
            location="Sevilla",
            services=["Revisiones"],
            main_goal="Consultas",
            desired_style=[],
        ),
        ux=WebsiteStructure(
            sections=[
                SectionSpec(name="Inicio", purpose="Oferta", required_content=[])
            ],
            navigation=["Inicio"],
            primary_cta=None,
            missing_content=[],
        ),
        capability_plan=CapabilityPlan(capabilities=[]),
        website_copy=WebsiteCopy(
            sections=[
                SectionCopy(
                    section_name="Inicio",
                    headline="Revisiones en Sevilla",
                    body="Consulta las opciones del taller.",
                    cta=None,
                    ready=True,
                    missing_requirements=[],
                )
            ]
        ),
        design=DesignSpec(
            visual_direction="Clara",
            color_palette=["#FFFFFF"],
            typography_direction="Sans",
            art_direction=ArtDirection(
                concept="Taller cercano", signature_element="Tipografía protagonista"
            ),
            section_designs=[
                SectionDesign(
                    section_name="Inicio",
                    layout="Split",
                    visual_notes="Legible",
                    required_inputs=[],
                    composition=composition,
                )
            ],
            missing_assets=[],
            missing_information=[],
        ),
    )
    assert (
        json.loads(build_design_context(state))["website_copy"]["sections"][0][
            "headline"
        ]
        == "Revisiones en Sevilla"
    )
    spec = build_website_spec(state)
    assert spec.art_direction.concept == "Taller cercano"
    assert spec.sections[0].composition == composition
    assert (
        spec.sections[0].composition is not state.design.section_designs[0].composition
    )


def test_copy_and_design_know_unavailable_functions():
    from context.context_builders import build_copy_context
    from specs.capability_spec import CapabilitySpec

    state = ProjectState(
        business=BusinessProfile(
            name="Prueba",
            business_type="taller",
            location="Sevilla",
            services=["Revisiones"],
            main_goal="Consultas",
            desired_style=[],
        ),
        ux=WebsiteStructure(
            sections=[], navigation=[], primary_cta=None, missing_content=[]
        ),
        capability_plan=CapabilityPlan(
            capabilities=[
                CapabilitySpec(type="contact_form", required=False, reason="Contacto")
            ]
        ),
    )
    for builder in (build_copy_context, build_design_context):
        constraints = json.loads(builder(state))["capability_constraints"]
        assert len(constraints) == 1
        assert constraints[0]["type"] == "contact_form"
        assert constraints[0]["ready"] is False
