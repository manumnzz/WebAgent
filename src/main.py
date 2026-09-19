from openai import OpenAI 
from dotenv import load_dotenv
from pydantic import BaseModel
from tools.tool_registry import execute_tool, get_tool_definitions
import json

load_dotenv()

client = OpenAI()

class BusinessProfile(BaseModel):
    name: str | None
    business_type: str
    location: str | None
    services: list[str]
    main_goal: str | None
    desired_style: list[str]

BUSINESS_AGENT_INSTRUCTIONS = """
Eres el Business Analyst de WebAgent.

Tu responsabilidad es analizar la descripción proporcionada
sobre un negocio y extraer la información relevante para
la futura creación de su página web.

Debes cumplir estas reglas:

- No inventes información.
- Diferencia claramente información explícita de suposiciones.
- Si desconoces un dato, indícalo.
- No diseñes la web.
- No escribas código.
- No generes el copy final de la página.
"""

business_description = """
Quiero crear una página web para Apex Barber Club.
No tengo más información sobre el negocio.
"""

tools = get_tool_definitions()

input_messages= [
        {
            "role": "system",
            "content": BUSINESS_AGENT_INSTRUCTIONS
        },
        {
            "role": "user",
            "content": business_description
        }
    ]

MAX_STEPS = 5
step = 0

business_profile = None


while step < MAX_STEPS:

    step += 1

    print(f"\n--- Paso {step} ---")


    response = client.responses.parse(
        model="gpt-5.6-luna",
        input=input_messages,
        tools=tools,
        text_format=BusinessProfile
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
            arguments=arguments
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

        business_profile = response.output_parsed

        print("\nBusinessAgent terminado:")
        print(business_profile)

        break