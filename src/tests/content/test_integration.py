
from content.models import WebsiteContent
from content.storage import (
    save_website_content,
    load_website_content,
)
from projects.workspace import build_project_workspace
from state.project_state import ProjectState


def test_project_state_supports_website_content():
    state = ProjectState()

    assert state.website_content is None

    state.website_content = WebsiteContent(
        business_name="Iron Garage"
    )

    assert state.website_content.business_name == "Iron Garage"


def test_project_state_content_is_independent():
    first = ProjectState()
    second = ProjectState()

    first.website_content = WebsiteContent(
        business_name="Iron Garage"
    )

    assert second.website_content is None


def test_content_can_be_saved_from_project_state(tmp_path):
    workspace = build_project_workspace(
        "iron-garage",
        projects_directory=tmp_path,
    )

    state = ProjectState(
        website_content=WebsiteContent(
            business_name="Iron Garage"
        )
    )

    save_website_content(
        state.website_content,
        workspace.website_content_path,
    )

    restored = load_website_content(
        workspace.website_content_path
    )

    assert restored == state.website_content


def test_content_is_not_saved_automatically(tmp_path):
    workspace = build_project_workspace(
        "iron-garage",
        projects_directory=tmp_path,
    )

    state = ProjectState(
        website_content=WebsiteContent(
            business_name="Iron Garage"
        )
    )

    assert state.website_content is not None
    assert not workspace.website_content_path.exists()
