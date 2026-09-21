import json

from openai import OpenAI

from agents.agent_config import AgentConfig
from tools.tool_registry import (
    get_tool_definitions,
    execute_tool
)


client = OpenAI()


def run_agent(
    agent: AgentConfig,
    user_input: str,
    max_steps: int = 5
):

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

        step += 1

        print(f"\n--- {agent.name} | Paso {step} ---")

        response = client.responses.parse(
            model=agent.model,
            input=input_messages,
            tools=tools,
            text_format=agent.output_schema
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
                allowed_tools=agent.allowed_tools
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

            return response.output_parsed

    print(
        f"\n{agent.name} alcanzó el máximo "
        f"de {max_steps} pasos."
    )

    return None