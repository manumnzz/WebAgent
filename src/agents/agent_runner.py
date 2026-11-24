import json

from openai import OpenAI

from pathlib import Path

from agents.metrics_storage import save_agent_metrics

from agents.agent_config import AgentConfig
from tools.tool_registry import (
    get_tool_definitions,
    execute_tool
)

from time import perf_counter

from agents.agent_metrics import AgentMetrics

from projects.workspace import ProjectWorkspace


def run_agent(
    agent: AgentConfig,
    user_input: str,
    max_steps: int = 10,
    *,
    workspace: ProjectWorkspace | None = None,
    metrics_path: Path | None = None,
):

    client = OpenAI(timeout=300.0, max_retries=1)

    input_messages = [
        {
            "role": "system",
            "content": agent.instructions
        },
        {
            "role": "user",
            "content": user_input
        }
    ]

    tools = get_tool_definitions(
        agent.allowed_tools
    )

    step = 0

    while step < max_steps:

        metrics = AgentMetrics()

        def persist_metrics():
            if metrics_path is not None:
                save_agent_metrics(
                    path=metrics_path,
                    agent_name=agent.name,
                    model=agent.model,
                    metrics=metrics,
                )

        step += 1

        print(f"\n--- {agent.name} | Paso {step} ---")

        start_time = perf_counter()

        response = client.responses.parse(
            model=agent.model,
            input=input_messages,
            tools=tools,
            text_format=agent.output_schema
        )

        duration = perf_counter() - start_time

        metrics.record(
            usage=response.usage,
            duration=duration,
        )

        print(
            f"\n[METRICS] {agent.name}"
            f"\nModelo: {agent.model}"
            f"\nLlamadas API: {metrics.api_calls}"
            f"\nTokens entrada: {metrics.input_tokens}"
            f"\nTokens salida: {metrics.output_tokens}"
            f"\nTokens razonamiento: {metrics.reasoning_tokens}"
            f"\nTiempo API: {metrics.api_duration_seconds:.2f}s"
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
                    "output": json.dumps(result)
                }
            )

        if not tool_called:

            print(f"\n{agent.name} terminado.")

            persist_metrics()

            return response.output_parsed

    print(
        f"\n{agent.name} alcanzó el máximo "
        f"de {max_steps} pasos."
    )

    persist_metrics()

    return None