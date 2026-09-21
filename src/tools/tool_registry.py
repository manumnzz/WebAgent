from tools.business_tools import (
    search_business,
    search_business_preferences
)


# ============================================================
# 2. DEFINICIONES DE LAS TOOLS QUE VERÁ EL MODELO
# ============================================================
# Esto NO ejecuta nada.
#
# Simplemente le explica al modelo:
#
# - cómo se llama la herramienta
# - para qué sirve
# - qué argumentos necesita
#
# Es como el "manual de instrucciones" de la herramienta
# para el LLM.


SEARCH_BUSINESS_DEFINITION = {
    "type": "function",
    "name": "search_business",
    "description":
        "Busca información disponible sobre un negocio a partir de su nombre.",
    "parameters": {
        "type": "object",
        "properties": {
            "business_name": {
                "type": "string",
                "description":
                    "Nombre exacto del negocio que se quiere buscar."
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


# ============================================================
# 3. TOOL_SPECS
# ============================================================
#
# Este es nuestro CATÁLOGO GLOBAL DE HERRAMIENTAS.
#
# Une las dos caras de cada tool:
#
# definition -> lo que conoce el MODELO
# handler    -> la función PYTHON que ejecuta la acción
#
# Este es el punto donde decimos:
#
# "La tool llamada search_business que conoce el modelo
#  corresponde realmente a la función Python search_business"


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


# ============================================================
# 4. TOOL_REGISTRY
# ============================================================
#
# El Registry sirve para encontrar rápidamente la función Python
# correspondiente al nombre que devuelve el modelo.
#
#
# TOOL_SPECS contiene mucha información:
#
# {
#     definition: {...},
#     handler: función
# }
#
#
# Pero cuando queremos EJECUTAR una tool solo necesitamos:
#
# nombre -> función
#
#
# Por eso generamos:
#
# {
#     "search_business": search_business,
#     "search_business_preferences": search_business_preferences
# }


TOOL_REGISTRY = {
    spec["definition"]["name"]: spec["handler"]
    for spec in TOOL_SPECS
}


# ============================================================
# 5. get_tool_definitions()
# ============================================================
#
# Esta función prepara las herramientas que vamos a enseñar
# a un agente concreto.
#
# IMPORTANTE:
#
# TOOL_SPECS contiene TODAS las tools de WebAgent.
#
# Pero no queremos que todos los agentes vean todas.
#
#
# Por ejemplo:
#
# BUSINESS_AGENT_TOOLS = [
#     "search_business",
#     "search_business_preferences"
# ]
#
#
# Entonces llamamos:
#
# get_tool_definitions(BUSINESS_AGENT_TOOLS)
#
#
# y esta función busca dentro de TOOL_SPECS únicamente
# las definitions de esas herramientas.
#
#
# Resultado:
#
# [
#     SEARCH_BUSINESS_DEFINITION,
#     SEARCH_BUSINESS_PREFERENCES_DEFINITION
# ]
#
#
# Eso es lo que finalmente enviamos al modelo.


def get_tool_definitions(tool_names: list[str]):

    return [
        spec["definition"]
        for spec in TOOL_SPECS
        if spec["definition"]["name"] in tool_names
    ]


# ============================================================
# 6. execute_tool()
# ============================================================
#
# Esta función es nuestro EJECUTOR GENÉRICO.
#
# Su trabajo es:
#
# 1. Comprobar si el agente tiene permiso.
# 2. Buscar qué función Python corresponde al nombre recibido.
# 3. Ejecutarla.
# 4. Devolver el resultado.
#
#
# Lo importante es que execute_tool NO conoce herramientas
# concretas.
#
# No hay:
#
# if tool_name == "search_business"
# if tool_name == "otra_tool"
#
# Por eso el sistema escala.


def execute_tool(
    tool_name: str,
    arguments: dict,
    allowed_tools: list[str]
):
    if tool_name not in allowed_tools:
        return {
            "success": False,
            "error":
                f"Tool '{tool_name}' no permitida para este agente."
        }


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