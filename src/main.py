from dotenv import load_dotenv

load_dotenv()

from tools.filesystem_tools import WEBSITE_ROOT
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

state = ProjectState()

business_description = """
Quiero crear una página para Apex Barber Club.
No tengo más información.
"""

# ============================================================
# BUSINESS AGENT
# ============================================================

state.business = run_agent(
    agent=BUSINESS_AGENT,
    user_input=business_description
)

print("\nResultado final:")
print(state.business)

# ============================================================
# UX AGENT
# ============================================================

ux_input = build_ux_context(state)

state.ux = run_agent(
    agent=UX_AGENT,
    user_input=ux_input
)

print("\nWebsite Structure:")
print(state.ux)

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
    user_input=developer_context
)

print("\n=== DEVELOPMENT RESULT ===")
print(state.development)

# ============================================================
# VALIDATOR
# ============================================================

state.validation = validate_website()

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
        user_input=repair_context
    )

    print("\n=== DEVELOPMENT RESULT ===")
    print(
        state.development.model_dump_json(indent=2)
    )

    state.validation = validate_website()

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