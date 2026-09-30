from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

WEBSITE_ROOT = PROJECT_ROOT / "output" / "website"

WRITE_FILE_DEFINITION = {
    "type": "function",
    "name": "write_file",
    "description": (
        "Crea o sobrescribe un archivo dentro del workspace "
        "de la web generada."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": (
                    "Ruta relativa del archivo dentro del workspace "
                    "de la web. Ejemplo: 'index.html' o 'css/styles.css'."
                )
            },
            "content": {
                "type": "string",
                "description": "Contenido completo que se escribirá en el archivo."
            }
        },
        "required": ["path", "content"],
        "additionalProperties": False
    }
}

READ_FILE_DEFINITION = {
    "type": "function",
    "name": "read_file",
    "description": (
        "Lee el contenido de un archivo existente dentro del "
        "workspace de la web generada."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": (
                    "Ruta relativa del archivo dentro del workspace "
                    "de la web. Ejemplo: 'index.html' o 'css/styles.css'."
                )
            }
        },
        "required": ["path"],
        "additionalProperties": False
    }
}

def write_file(path: str, content: str):

    target_path = (WEBSITE_ROOT / path).resolve()

    if not target_path.is_relative_to(WEBSITE_ROOT.resolve()):
        return {
            "success": False,
            "error": "Ruta no permitida."
        }

    target_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    target_path.write_text(
        content,
        encoding="utf-8"
    )

    return {
        "success": True,
        "path": path
    }

def read_file(path: str):

    target_path = (WEBSITE_ROOT / path).resolve()

    if not target_path.is_relative_to(WEBSITE_ROOT.resolve()):
        return {
            "success": False,
            "error": "Ruta no permitida."
        }

    if not target_path.is_file():
        return {
            "success": False,
            "error": f"Archivo no encontrado: {path}"
        }

    content = target_path.read_text(
        encoding="utf-8"
    )

    return {
        "success": True,
        "path": path,
        "content": content
    }



    