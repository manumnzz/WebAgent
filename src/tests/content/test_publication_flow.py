import json
import runpy
import sys
from datetime import date, timedelta
from html import escape
from io import BytesIO
from pathlib import Path
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from agents import agent_runner
from agents.business_agent import BusinessProfile
from agents.copy_agent import SectionCopy, WebsiteCopy
from agents.design_agent import DesignSpec, SectionDesign
from agents.developer_agent import DevelopmentResult
from agents.ux_agent import SectionSpec, UXResult, WebsiteStructure
from api import main as project_api
from content.models import WebsiteContent
from content.storage import load_website_content, publish_content_edit
from intake.api import create_intake_app
from projects import workspace as project_workspace
from projects.repair import repair_project
from specs.capability_spec import CapabilityPlan, CapabilitySpec
from specs.storage import load_website_spec
from tools.filesystem_tools import write_file
from validation.validator import validate_website


PRIVATE_NOTE = "PRIVATE-NOTES-ONLY"
EDITORIAL = "Trabajo hecho con calma"
PROJECTS = ("taller", "estudio")
DAY_KEYS = ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday")
PRESENTATION_FILES = ("index.html", "styles.css", "script.js", "website-content.js")
ROOT = Path(__file__).resolve().parents[3]

CONTENT_MARKUP = """
<main data-capability-zone="content">
  <div data-content-list="services" hidden>
    <template data-content-item>
      <article>
        <h2 data-content-field="name"></h2>
        <p data-content-field="description"></p>
        <p data-content-field="price"></p>
      </article>
    </template>
  </div>
  <ul data-content-list="opening_hours" hidden>
    <template data-content-item>
      <li><span data-content-field="day"></span> <span data-content-field="hours"></span></li>
    </template>
  </ul>
  {gallery}
</main>
<section data-capability-zone="contact">
  <strong data-content-text="business_name" hidden></strong>
  <p data-content-text="address" hidden></p>
  <p data-content-text="whatsapp" hidden></p>
  <a data-content-link="tel" hidden><span data-content-text="phone"></span></a>
  <a data-content-link="email" hidden><span data-content-text="email"></span></a>
  {contact_form}
  {maps}
</section>
"""


def fake_agent(agent, user_input, *, workspace=None):
    if agent.name == "business_agent":
        return BusinessProfile(
            name="Negocio",
            business_type="local",
            location=None,
            services=[],
            main_goal=None,
            desired_style=[],
        )
    if agent.name == "ux_agent":
        requested = json.loads(user_input)["requested_features"]
        return UXResult(
            structure=WebsiteStructure(
                sections=[SectionSpec(name="Inicio", purpose="Presentación", required_content=[])],
                navigation=[],
                primary_cta=None,
                missing_content=[PRIVATE_NOTE],
            ),
            capability_plan=CapabilityPlan(capabilities=[
                CapabilitySpec(type=feature, required=True, reason="Solicitada")
                for feature in requested
            ]),
        )
    if agent.name == "copy_agent":
        return WebsiteCopy(sections=[
            SectionCopy(
                section_name="Inicio", headline=EDITORIAL, body="Un negocio local.",
                cta=None, ready=True, missing_requirements=[],
            ),
        ])
    if agent.name == "design_agent":
        return DesignSpec(
            visual_direction="Sencilla", color_palette=[], typography_direction="Legible",
            section_designs=[
                SectionDesign(section_name="Inicio", layout="simple", visual_notes="", required_inputs=[]),
            ],
            missing_assets=[],
            missing_information=[],
        )

    assert agent.name == "developer_agent"
    assert "WEBSITE_CONTENT_RUNTIME:" in user_input
    assert not workspace.website_content_path.exists()
    assert write_file("content.json", "{}", website_root=workspace.website_directory)["success"] is False
    spec = json.JSONDecoder().raw_decode(user_input.split("WEBSITE_SPEC:", 1)[1].strip())[0]
    snippets = json.JSONDecoder().raw_decode(
        user_input.split("PREBUILT_CAPABILITY_IMPLEMENTATIONS:", 1)[1].strip()
    )[0]
    capabilities = {snippet["type"]: snippet["html"] for snippet in snippets}
    body = CONTENT_MARKUP.format(**{
        name: capabilities.get(name, "") for name in ("gallery", "contact_form", "maps")
    })
    headline = escape(spec["sections"][0]["headline"])
    html = f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8"><title>Proyecto</title>
<link rel="stylesheet" href="styles.css">
<script src="website-content.js" defer></script></head>
<body><header data-capability-zone="hero"><h1>{headline}</h1>
{capabilities.get("booking", "")}</header>
{body}
<aside data-capability-zone="floating">{capabilities.get("whatsapp", "")}</aside>
<script src="script.js"></script></body></html>
"""
    for name, text in {
        "index.html": html, "styles.css": "[hidden]{display:none!important}",
        "script.js": '"use strict";',
    }.items():
        assert write_file(name, text, website_root=workspace.website_directory)["success"]
    return DevelopmentResult(files_created=[], files_modified=[], implementation_notes=[])


def prepare_projects(root, monkeypatch):
    monkeypatch.setattr(project_workspace, "PROJECT_ROOT", root)
    monkeypatch.setattr(project_api, "PROJECT_ROOT", root)
    monkeypatch.setattr(agent_runner, "run_agent", fake_agent)
    calendar = Mock()
    calendar.freebusy.return_value.query.return_value.execute.return_value = {
        "calendars": {"primary": {"busy": []}},
    }
    calendar.events.return_value.insert.return_value.execute.return_value = {"id": "evento-local"}
    monkeypatch.setattr(project_api, "build_google_calendar_service", lambda **_: calendar)

    intake = create_intake_app(root / "intake")
    workspaces = {}
    apps = {}
    for name in PROJECTS:
        bookings = name == "taller"
        payload = {
            "business_name": name.title(),
            "business_description": "Negocio de prueba.",
            "additional_notes": PRIVATE_NOTE,
            "services": ["Servicio principal", "Otro servicio"],
            "service_details": [{"name": "Servicio principal", "price": "40 €" if bookings else "20 €"}],
            "contact": {"email": "info@example.org", "address": "Calle Original", "phone": "+34 600 111 222",
                        "whatsapp": "+34 600 111 222"},
            "opening_hours": [{"weekday": "monday", "hours": "09:00–14:00"}],
            "requested_features": ["gallery", "whatsapp", "maps", "contact_form"],
        }
        if bookings:
            payload["requested_features"].append("booking")
            payload["appointment_types"] = ["Cita independiente"]
            payload["booking"] = {
                "timezone": "Europe/Madrid",
                "slot_interval_minutes": 30,
                "service_durations": {"cita-independiente": 30},
                "weekly_schedule": [
                    {"weekday": day, "ranges": [{"start": "10:00", "end": "14:00"}]}
                    for day in DAY_KEYS
                ],
            }
        with TestClient(intake) as client:
            receipt = client.post("/intake", json=payload)
            assert receipt.status_code == 201, receipt.text
            submission_id = receipt.json()["submission_id"]
            if bookings:
                upload = BytesIO()
                Image.new("RGB", (32, 32), "blue").save(upload, format="PNG")
                media = client.post(
                    f"/intake/{submission_id}/media",
                    files=[
                        ("gallery", ("foto.png", upload.getvalue(), "image/png")),
                        ("logo", ("logo.png", upload.getvalue(), "image/png")),
                    ],
                )
                assert media.status_code == 201, media.text

        project_input = root / "intake" / submission_id / "project_input.json"
        monkeypatch.setattr(sys, "argv", ["main.py", "--project-id", name, "--input", str(project_input)])
        result = runpy.run_path(str(ROOT / "src" / "main.py"), run_name="__main__")
        assert result["state"].validation.is_valid, result["state"].validation
        workspaces[name] = result["workspace"]
        monkeypatch.setenv("WEBAGENT_PROJECT_ID", name)
        apps[name] = project_api.create_project_app()

    return workspaces, apps, calendar


def edit_taller(workspace, draft):
    content = load_website_content(workspace.website_content_path)
    payload = content.model_dump(mode="json")
    payload["services"].reverse()
    payload["services"][1].update({"name": "Servicio actualizado", "price": "55 €"})
    payload["services"].append({"name": "Un servicio nuevo"})
    payload["contact"].update({
        "address": "Calle Nueva", "phone": "+34 600 333 444", "email": "nuevo@example.org",
        "whatsapp": "+34 600 333 444",
    })
    payload["opening_hours"] = [{"weekday": "tuesday", "hours": "16:00–20:00"}]
    payload["gallery"][0]["alt"] = "Foto actualizada"
    draft.write_text(json.dumps(payload), encoding="utf-8")
    publish_content_edit(workspace, draft)


def test_two_generated_projects_publish_edit_without_agents(tmp_path, monkeypatch):
    workspaces, apps, calendar = prepare_projects(tmp_path, monkeypatch)

    def unexpected_agent(*args, **kwargs):
        pytest.fail("Una edición de contenido no debe ejecutar agentes.")

    monkeypatch.setattr(agent_runner, "run_agent", unexpected_agent)
    taller, estudio = [workspaces[name] for name in PROJECTS]
    with TestClient(apps["taller"]) as first, TestClient(apps["estudio"]) as second:
        presentation = {name: first.get(f"/{name}").content for name in PRESENTATION_FILES}
        untouched = second.get("/content.json").content
        booking = first.get("/booking/services").json()
        booking_config = taller.booking_configuration_path.read_bytes()
        public_before = first.get("/content.json").json()
        assert len(public_before["gallery"]) == 1
        assert len(list((taller.website_directory / "assets").iterdir())) == 2
        assert PRIVATE_NOTE not in json.dumps(public_before)
        assert EDITORIAL not in json.dumps(public_before)

        edit_taller(taller, tmp_path / "borrador.json")

        public = first.get("/content.json").json()
        assert set(public) == set(WebsiteContent.model_fields)
        assert public["services"][1]["name"] == "Servicio actualizado"
        assert public["services"][1]["price"] == "55 €"
        assert public["services"][1]["id"] == public_before["services"][0]["id"]
        assert public["services"][0]["id"] == public_before["services"][1]["id"]
        assert public["services"][2]["id"]
        assert set(public["gallery"][0]) == {"path", "alt"}
        assert first.get("/" + public["gallery"][0]["path"]).status_code == 200
        assert public["opening_hours"] == [{"weekday": "tuesday", "hours": "16:00–20:00"}]
        assert {name: first.get(f"/{name}").content for name in PRESENTATION_FILES} == presentation
        assert second.get("/content.json").content == untouched
        assert "20 €" in second.get("/content.json").text
        assert first.get("/reservar").status_code == 200
        assert first.get("/booking/services").json() == booking
        assert booking[0]["id"] == "cita-independiente"
        assert taller.booking_configuration_path.read_bytes() == booking_config

        day = date.today() + timedelta(days=2)
        reservation = first.post("/booking", json={
            "service_id": "cita-independiente", "booking_date": day.isoformat(),
            "booking_time": "10:00", "first_name": "Persona", "last_name": "Prueba",
            "email": "cliente@example.org",
        })
        assert reservation.status_code == 201, reservation.text
        event = calendar.events.return_value.insert.call_args.kwargs["body"]
        assert event["location"] == "Calle Nueva"
        assert "nuevo@example.org" in event["description"]

        for client in (first, second):
            for private_path in ("/config/website_spec.json", "/config/booking.json", "/.env", "/token.json"):
                assert client.get(private_path).status_code == 404
        assert second.get("/reservar").status_code == 404
        assert not estudio.booking_configuration_path.exists()


def test_publication_rejects_bad_drafts_without_replacing_content(tmp_path, monkeypatch):
    projects, _, _ = prepare_projects(tmp_path, monkeypatch)
    workspace = projects["taller"]
    original = workspace.website_content_path.read_bytes()
    valid = json.loads(original)
    draft = tmp_path / "borrador.json"
    invalid_changes = (
        {"gallery": [{"path": "assets/ausente.jpg"}]},
        {"gallery": [{"path": "../token.json"}]},
        {"services": [{"id": "id-cambiado", "name": "Renombrado"}]},
        {"services": [{"name": "Nuevo", "price": "Información pendiente de completar"}]},
        {"contact": {"access_token": PRIVATE_NOTE}},
        {"booking": {"credentials": PRIVATE_NOTE}},
    )
    for change in invalid_changes:
        draft.write_text(json.dumps(valid | change), encoding="utf-8")
        with pytest.raises(ValueError):
            publish_content_edit(workspace, draft)
        assert workspace.website_content_path.read_bytes() == original


def test_repair_preserves_the_published_content_and_checks_bindings(tmp_path, monkeypatch):
    projects, _, _ = prepare_projects(tmp_path, monkeypatch)
    source = projects["estudio"]
    content = source.website_content_path.read_bytes()
    html = source.website_directory / "index.html"
    valid = html.read_text()
    html.write_text(valid.replace('data-content-field="price"', ""))
    spec = load_website_spec(source.website_spec_path)
    validation = validate_website(
        website_root=source.website_directory,
        website_content=load_website_content(source.website_content_path),
        capabilities=spec.capabilities,
    )
    assert any(error.code == "invalid_content_binding" for error in validation.errors)

    def run_repair(context, destination):
        assert "WEBSITE_CONTENT_RUNTIME:" in context
        assert "invalid_content_binding" in context
        (destination.website_directory / "index.html").write_text(valid)
        return DevelopmentResult(files_created=[], files_modified=["index.html"], implementation_notes=[])

    repaired = project_workspace.build_project_workspace("reparado")
    report = repair_project(source, repaired, developer_runner=run_repair)
    assert report.validation.is_valid
    assert repaired.website_content_path.read_bytes() == content
    assert source.website_content_path.read_bytes() == content
    assert html.read_text() != valid


def test_cli_publishes_first_gallery_image_and_accepts_legacy_v2(tmp_path, monkeypatch):
    projects, apps, _ = prepare_projects(tmp_path, monkeypatch)
    taller, estudio = [projects[name] for name in PROJECTS]
    payload = json.loads(estudio.website_content_path.read_bytes())
    payload.pop("gallery")
    payload.pop("opening_hours")
    legacy_content = WebsiteContent.model_validate(payload)
    assert legacy_content.gallery == [] and legacy_content.opening_hours == []

    image = load_website_content(taller.website_content_path).gallery[0]
    destination = estudio.website_directory / "assets" / "fachada.webp"
    destination.parent.mkdir()
    destination.write_bytes((taller.website_directory / image.path).read_bytes())
    payload["gallery"] = [{"path": "assets/fachada.webp", "alt": "Fachada"}]
    draft = tmp_path / "galeria.json"
    draft.write_text(json.dumps(payload))
    original_html = (estudio.website_directory / "index.html").read_bytes()
    monkeypatch.setattr(sys, "argv", ["content", "--project-id", "estudio", str(draft)])

    runpy.run_module("content", run_name="__main__")

    with TestClient(apps["estudio"]) as client:
        public = client.get("/content.json").json()
        assert public["gallery"] == payload["gallery"]
        assert client.get("/assets/fachada.webp").status_code == 200
        assert client.get("/index.html").content == original_html
