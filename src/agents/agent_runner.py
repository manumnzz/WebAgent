import json
import base64
from pathlib import Path
from collections.abc import Sequence

from openai import OpenAI

from agents.agent_config import AgentConfig
from agents.model_policy import resolve_model, resolve_reasoning
from tools.tool_registry import get_tool_definitions, execute_tool

from projects.workspace import ProjectWorkspace


def image_content(paths: Sequence[Path]) -> list[dict]:
    if len(paths) > 8:
        raise ValueError("Se admiten como máximo ocho imágenes por revisión.")
    content = []
    for path in paths:
        mime = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".webp": "image/webp",
        }.get(path.suffix.lower())
        if not mime or not path.is_file() or path.stat().st_size > 12_000_000:
            raise ValueError(f"Imagen no válida o demasiado grande: {path.name}")
        content.extend(
            [
                {"type": "input_text", "text": f"Imagen: {path.name}"},
                {
                    "type": "input_image",
                    "detail": "high",
                    "image_url": f"data:{mime};base64,"
                    + base64.b64encode(path.read_bytes()).decode("ascii"),
                },
            ]
        )
    return content


def run_agent(
    agent: AgentConfig,
    user_input: str,
    max_steps: int = 10,
    *,
    workspace: ProjectWorkspace | None = None,
    image_paths: Sequence[Path] = (),
):

    client = OpenAI(timeout=300.0, max_retries=1)
    model = resolve_model(agent)
    reasoning = resolve_reasoning(agent, model)
    input_messages = [
        {"role": "system", "content": agent.instructions},
        {
            "role": "user",
            "content": (
                [{"type": "input_text", "text": user_input}]
                + image_content(image_paths)
            ),
        },
    ]

    tools = get_tool_definitions(agent.allowed_tools)

    step = 0

    while step < max_steps:
        step += 1

        print(f"\n--- {agent.name} | {model} | Paso {step} ---", flush=True)

        response = client.responses.parse(
            model=model,
            input=input_messages,
            tools=tools,
            text_format=agent.output_schema,
            **reasoning,
        )

        if response.usage is not None:
            print(
                f"Tokens: entrada={response.usage.input_tokens}, "
                f"salida={response.usage.output_tokens}",
                flush=True,
            )
        input_messages += response.output

        tool_called = False

        for item in response.output:
            if item.type != "function_call":
                continue

            tool_called = True

            arguments = json.loads(item.arguments)

            result = execute_tool(
                tool_name=item.name,
                arguments=arguments,
                allowed_tools=agent.allowed_tools,
                workspace=workspace,
            )

            print(f"Tool solicitada: {item.name}")
            print("Resultado:", result)

            input_messages.append(
                {
                    "type": "function_call_output",
                    "call_id": item.call_id,
                    "output": json.dumps(result),
                }
            )

        if not tool_called:
            print(f"\n{agent.name} terminado.")

            return response.output_parsed

    print(f"\n{agent.name} alcanzó el máximo de {max_steps} pasos.")

    return None
