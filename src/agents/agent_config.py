from dataclasses import dataclass

@dataclass
class AgentConfig:
    name: str
    model: str
    instructions: str
    allowed_tools: list[str]
    output_schema: type