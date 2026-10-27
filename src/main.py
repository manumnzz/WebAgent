from dotenv import load_dotenv

load_dotenv()

from pathlib import Path

import argparse

from intake.loader import load_project_input
from intake.business_adapter import (
    apply_explicit_business_data,
    build_business_input,
)
from capabilities.capability_input_resolver import (
    resolve_business_capability_inputs,
)
from capabilities.models.review import (
    ReviewData,
)
from capabilities.booking.configuration_finalizer import (
    finalize_booking_configuration,
)
from capabilities.booking.config_writer import (
    save_booking_configuration,
)
from capabilities.models.booking import (
    BookingBusinessInfo,
)
from projects.workspace import build_project_workspace
from state.project_state import ProjectState
from context.context_builders import (
    build_ux_context,
    build_copy_context,
    build_design_context,
    build_developer_context,
    build_developer_repair_context)
from specs.website_spec_builder import build_website_spec
from agents.agent_runner import run_agent
from agents.business_agent import BUSINESS_AGENT
from agents.ux_agent import UX_AGENT
from agents.copy_agent import COPY_AGENT
from agents.design_agent import DESIGN_AGENT
from agents.developer_agent import DEVELOPER_AGENT
from validation.validator import validate_website

from intake.booking_adapter import (
    build_booking_draft_from_input,
)
from capabilities.booking.configuration_readiness import (
    get_booking_missing_information,
)
from media.publishing import publish_submission_media

state = ProjectState()

state.capability_inputs.gallery_assets = []

state.capability_inputs.review_data = []

project_root = Path(__file__).resolve().parent.parent

parser = argparse.ArgumentParser(
    description="Genera una web a partir de un encargo."
)

parser.add_argument(
    "--input",
    type=Path,
    default=project_root / "config" / "project_input.json",
    help="Ruta al archivo JSON del encargo.",
)

parser.add_argument(
    "--project-id",
    required=True,
    help="Identificador del proyecto donde se guardará la web.",
)

args = parser.parse_args()

try:
    workspace = build_project_workspace(
        args.project_id,
    )
except ValueError as error:
    parser.error(str(error))

state.project_input = load_project_input(
    args.input,
)

website_has_files = (
    workspace.website_directory.exists()
    and any(workspace.website_directory.iterdir())
)

if (
    website_has_files
    or workspace.booking_configuration_path.exists()
):
    parser.error(
        "Este proyecto ya contiene una web o configuración. "
        "Usa un identificador nuevo para esta generación."
    )

workspace.create_directories()

state.available_media = publish_submission_media(
    submission_directory=args.input.resolve().parent,
    workspace=workspace,
)

state.capability_inputs.gallery_assets = [
    asset.path
    for asset in state.available_media
    if asset.role == "gallery"
]

print("\nProyecto:", workspace.project_id)
print("Carpeta de la web:", workspace.website_directory)

print(
    "\nEncargo cargado:",
    state.project_input.business_name,
)

# ============================================================
# BUSINESS AGENT
# ============================================================

business_input = build_business_input(
    state.project_input
)

business_result = run_agent(
    agent=BUSINESS_AGENT,
    user_input=business_input,
)

state.business = apply_explicit_business_data(
    business=business_result,
    project_input=state.project_input,
)

print("\nResultado final:")
print(state.business)

# ============================================================
# BOOKING: CONFIGURACIÓN APORTADA POR EL CLIENTE
# ============================================================

state.booking_configuration_draft = (
    build_booking_draft_from_input(
        project_input=state.project_input,
    )
)

draft = state.booking_configuration_draft

if draft is None:
    print("\nNo hay opciones de cita configuradas.")

else:
    missing = get_booking_missing_information(
        draft
    )

    if not missing.is_complete:
        print("\n=== BOOKING: INFORMACIÓN PENDIENTE ===")
        print(
            missing.model_dump_json(
                indent=2
            )
        )

    else:
        booking_configuration = (
            finalize_booking_configuration(
                draft
            )
        )

        booking_configuration.business = BookingBusinessInfo(
            name=state.business.name,
            phone=state.business.contact.phone,
            whatsapp=state.business.contact.whatsapp,
            email=state.business.contact.email,
            address=state.business.contact.address,
        )

        state.capability_inputs.booking_configuration = (
            booking_configuration
        )

        save_booking_configuration(
            booking_configuration,
            path=workspace.booking_configuration_path,
        )
        print("\n=== BOOKING CONFIGURATION ===")
        print(
            booking_configuration.model_dump_json(
                indent=2
            )
        )

state.capability_inputs = (
    resolve_business_capability_inputs(
        state.business,
        state.capability_inputs,
    )
)

# ============================================================
# UX AGENT
# ============================================================

ux_input = build_ux_context(state)

ux_result = run_agent(
    agent=UX_AGENT,
    user_input=ux_input
)

state.ux = ux_result.structure
state.capability_plan = ux_result.capability_plan

print("\n=== WEBSITE STRUCTURE ===")
print(state.ux.model_dump_json(indent=2))

print("\n=== CAPABILITY PLAN ===")
print(state.capability_plan.model_dump_json(indent=2))

# ============================================================
# COPY AGENT
# ============================================================

copy_input = build_copy_context(state)

state.website_copy = run_agent(
    agent=COPY_AGENT,
    user_input=copy_input
)

print("\nWebsite Copy:")
print(state.website_copy)

# ============================================================
# DESIGN AGENT
# ============================================================

design_input = build_design_context(state)

state.design = run_agent(
    agent=DESIGN_AGENT,
    user_input=design_input
)

print("\nDesign Spec:")
print(state.design)


# ============================================================
# WEBSITE SPEC
# ============================================================


state.website_spec = build_website_spec(state)

print("\nWEBSITE SPEC:")
print(
    state.website_spec.model_dump_json(indent=2)
)

# ============================================================
# DEVELOPMENT AGENT /// GENERATE ///
# ============================================================

developer_context = build_developer_context(state)

state.development = run_agent(
    agent=DEVELOPER_AGENT,
    user_input=developer_context,
    workspace=workspace,
)

print("\n=== DEVELOPMENT RESULT ===")
print(state.development)

# ============================================================
# VALIDATOR
# ============================================================

state.validation = validate_website(
    state.capability_inputs.booking_configuration,
    website_root=workspace.website_directory,
    capabilities=state.website_spec.capabilities,
)

print("\n--- VALIDATION ---")
print(state.validation.model_dump_json(indent=2))

# ============================================================
# DEVELOPMENT AGENT /// REPAIR ///
# ============================================================

MAX_REPAIR_ATTEMPTS = 2

repair_attempt = 0

while (
    not state.validation.is_valid
    and repair_attempt < MAX_REPAIR_ATTEMPTS
):
    
    repair_attempt += 1

    print(f"\n=== REPAIR {repair_attempt}/{MAX_REPAIR_ATTEMPTS} ===")

    repair_context = build_developer_repair_context(state)

    state.development = run_agent(
        agent=DEVELOPER_AGENT,
        user_input=repair_context,
        workspace=workspace,
    )

    print("\n=== DEVELOPMENT RESULT ===")
    print(
        state.development.model_dump_json(indent=2)
    )

    state.validation = validate_website(
        state.capability_inputs.booking_configuration,
        website_root=workspace.website_directory,
        capabilities=state.website_spec.capabilities,
    )

    print(
        f"\n--- VALIDATION AFTER REPAIR {repair_attempt} ---"
    )

    print(
        state.validation.model_dump_json(indent=2)
    )

# ============================================================
# FINAL RESULT
# ============================================================

if state.validation.is_valid:
    print("\n=== WEBSITE VALID ===")
    print("La web ha superado la validación.")

else: 

    print("\n=== REPAIR LIMIT REACHED ===")
    print(
        f"No se pudo validar la web despues de "
        f"{repair_attempt} intento(s) de reparación."
    )

    print("\nErrores restantes:")

    for error in state.validation.errors:
        print(
            f"- [{error.code}] "
            f"{error.file}: {error.message}"
        )
