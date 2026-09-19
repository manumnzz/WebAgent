from tools.business_tools import (search_business, search_business_preferences)

#Definición de cada función (Fuente de verdad conjunta (Python + Modelo))
SEARCH_BUSINESS_DEFINITION = {
    "type": "function",
    "name": "search_business",
    "description": "Busca información disponible sobre un negocio a partir de su nombre.",
    "parameters": {
        "type": "object",
        "properties": {
            "business_name": {
                "type": "string",
                "description": "Nombre exacto del negocio que se quiere buscar."
            }
        },
        "required": ["business_name"],
        "additionalProperties": False
    },
    "strict": True
}

SEARCH_BUSINESS_PREFERENCES_DEFINITION = {
    "type": "function",
    "name": "search_business_preferences",
    "description": (
        "Busca el objetivo principal y las preferencias de estilo "
        "disponibles sobre un negocio."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "business_name": {
                "type": "string",
                "description": "Nombre exacto del negocio."
            }
        },
        "required": ["business_name"],
        "additionalProperties": False
    },
    "strict": True
}

#Describe completamente qué herramientas existen
TOOL_SPECS = [
    {
        "definition": SEARCH_BUSINESS_DEFINITION,
        "handler": search_business
    },
    {
        "definition": SEARCH_BUSINESS_PREFERENCES_DEFINITION,
        "handler": search_business_preferences
    }
]

#Permite encontrar qué función Python ejecutar a partir del nombre de la tool
TOOL_REGISTRY = {
    spec["definition"]["name"]: spec["handler"]
    for spec in TOOL_SPECS
}

#Función que nos devuelve lo que el modelo necesita para utilizar las herramientas
def get_tool_definitions():
    return [
        spec["definition"]
        for spec in TOOL_SPECS
    ]


def execute_tool(tool_name: str, arguments: dict):
    tool = TOOL_REGISTRY.get(tool_name)

    if tool is None:
        return {
            "success": False,
            "error": f"Tool '{tool_name}' no encontrada."
        }

    try:
        return tool(**arguments)

    except Exception as error:
        return {
            "success": False,
            "error": str(error)
        }