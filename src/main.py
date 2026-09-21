from dotenv import load_dotenv

load_dotenv()

from state.project_state import ProjectState
from context.context_builders import (build_ux_context, build_copy_context, build_design_context)
from specs.website_spec_builder import build_website_spec
from agents.agent_runner import run_agent
from agents.business_agent import BUSINESS_AGENT
from agents.ux_agent import UX_AGENT
from agents.copy_agent import COPY_AGENT
from agents.design_agent import DESIGN_AGENT

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