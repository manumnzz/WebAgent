# Calidad visual de WebAgent

La skill frontend-design sigue siendo la base de criterio. El pipeline la convierte ahora en decisiones persistentes y evidencia: copy real → dirección de arte y composición → implementación → validación técnica → capturas → crítica visual → corrección acotada → comparación.

## Instalación

Desde la raíz del repositorio:

```bash
.venv/bin/python -m pip install -r requirements-visual.txt
.venv/bin/python -m playwright install chromium
```

Playwright y Chromium son opcionales para los tests unitarios y la generación sin revisión. `make generar` activa la revisión visual y comprueba el navegador antes de gastar llamadas en la generación. Si el sistema impide lanzar Chromium, ejecuta estos comandos desde una terminal local con acceso al navegador. No se declara éxito visual cuando falla la captura.

## Uso

- `make generar`: nueva generación, con textos y dirección de arte mejorados; hasta dos correcciones visuales tras la validación técnica.
- `make capturas`: seleccionar una web y obtener capturas/mediciones, sin llamadas al modelo.
- `make mejorar`: seleccionar una generación con contrato guardado y mejorar una copia; conserva el original.
- `make reparar`: sigue corrigiendo exclusivamente errores técnicos.

Comandos directos:

```bash
.venv/bin/python src/visual_quality.py --source-project-id dima-design-03
.venv/bin/python src/visual_quality.py --source-project-id dima-design-03 --project-id dima-visual-01 --improve
# Solo evaluación, sin modificaciones (sí consume una llamada de visión):
.venv/bin/python src/visual_quality.py --source-project-id dima-design-03 --project-id dima-review-01 --improve --max-attempts 0
# Generación sin revisión visual:
.venv/bin/python src/main.py --input RUTA_AL_ENCARGO --project-id NUEVO_ID
```

La primera evaluación consume una llamada. Cada intento de mejora añade la conversación de DeveloperAgent (máximo 12 pasos) y otra evaluación visual. Hay dos intentos por defecto y un máximo permitido de tres. Se detiene si alcanza el umbral, empeora o introduce errores técnicos. Las peticiones tienen timeout y reintentos acotados. La nota es una estimación del modelo, no una medición objetiva de gusto ni una garantía comercial.

## Qué cambia en el diseño

- CopyAgent produce títulos y acciones más breves, con menos repetición.
- DesignAgent recibe el copy real y hasta cuatro imágenes del encargo, además de metadatos y la skill original.
- `art_direction` registra alternativas, elección justificada, gesto memorable, jerarquía, ritmo y uso de imágenes.
- Cada sección conserva `composition`: escritorio, móvil, foco, ancho de lectura, superficie, rutas y encuadre.
- El sistema tipográfico incluye escala móvil/escritorio, interlineados y ancho de lectura.
- La navegación interna a una solicitud de presupuesto se acepta solo si el ancla conduce a la acción real de Booking; se rechazan destinos externos, ciclos y anclas vacías.
- DeveloperAgent recibe hasta cuatro imágenes reales y reglas para columnas sin desbordamiento, fuentes legibles y contenido visible sin JavaScript.
- Los contratos antiguos siguen cargándose con valores por defecto; no es necesario regenerarlos para `make mejorar`. Un contrato antiguo no adquiere una nueva dirección de arte retroactivamente.

## Qué se verifica

Capturas de escritorio (1440px) y móvil (390px), más mediciones a 768px y 360px. Primera pantalla y página completa; un resumen visual limita el coste de imágenes en el modelo. Las páginas de más de 14000px se marcan como incompletas, no como aprobadas. Se recorren los bloques para activar imágenes lazy y observers. Se espera la carga de fuentes y se reduce movimiento para capturas reproducibles. Se registra overflow horizontal, imágenes rotas, errores JavaScript, texto pequeño y contenido oculto. Otra carga sin JavaScript comprueba la lectura básica.

La revisión evalúa identidad, jerarquía, tipografía, composición, uso de imágenes y móvil. Exige al menos 8/10 en cada dimensión, ningún problema alto y ningún bloqueo del navegador. Cada incidencia indica evidencia, zona, corrección y criterio de aceptación.

Una corrección ocurre en un directorio temporal. Solo sustituye la versión anterior si sigue siendo técnicamente válida, no añade bloqueos, no aumenta problemas graves, no degrada una dimensión más de un punto y mejora la nota o elimina bloqueos sin bajar la nota. Un fallo conserva la mejor versión aceptada. Se guardan informes y capturas de los intentos para poder comparar.

## Informes

Todo se guarda fuera del directorio público `website/`:

- `config/screenshots/<id>/`: capturas sin evaluación.
- `config/visual-review/<id>/baseline/` y `attempt-N/`: evidencia de cada versión.
- `config/visual-review/<id>/report.json`: informe de la ejecución.
- `config/visual_report.json`: último informe.

`passed` significa que cumple el criterio automático; `needs_review`, que queda trabajo visual pendiente; `error`, que no pudo completarse. El CLI devuelve un estado distinto de cero si la calidad visual no se aprobó. Las webs técnicamente válidas siguen disponibles para revisar.

## Modelos

El perfil predeterminado `studio` usa GPT-6 Astra para copy, diseño, desarrollo y evaluación visual. BusinessAgent y UXAgent conservan sus modelos. El desarrollo usa razonamiento alto; copy, diseño y evaluación usan medio para acotar latencia. Cambiar el perfil cambia coste y latencia; no se hace fallback silencioso a un modelo inferior si el elegido falla.

```bash
# Calidad alta equilibrada
WEBAGENT_QUALITY_PROFILE=quality make generar
# Prioridad máxima al resultado visual (predeterminado)
WEBAGENT_QUALITY_PROFILE=studio make generar
# Modelos originales del repositorio
WEBAGENT_QUALITY_PROFILE=economy make generar
```

`studio` usa GPT-6 Astra en las cuatro etapas creativas. La [documentación oficial de modelos](https://developers.openai.com/api/docs/models) describe Astra como el más capaz y Sol como el equilibrio entre capacidad y coste. Ambos aparecieron en el listado de modelos accesibles de la cuenta durante la comprobación; el acceso puede cambiar.

Puedes fijar modelo y razonamiento por agente en `.env`; tienen prioridad sobre los perfiles:

- `WEBAGENT_COPY_AGENT_MODEL`
- `WEBAGENT_DESIGN_AGENT_MODEL`
- `WEBAGENT_DEVELOPER_AGENT_MODEL`
- `WEBAGENT_VISUAL_REVIEW_AGENT_MODEL`
- El correspondiente sufijo `_REASONING` acepta `low`, `medium`, `high`, `xhigh` o `max` (el modelo elegido debe admitirlo).

La calidad debe compararse con evidencia, no inferirse del precio. El modelo de diseño y el de revisión deben admitir imágenes. Para un benchmark útil usa al menos tres negocios distintos, con y sin fotografías, compara capturas a igual tamaño y registra preferencia humana, errores, tiempo y consumo.

## Límites y validación de esta entrega

Las pruebas unitarias cubren conservación del contrato, propagación del copy y composición, aceptación, descarte, límites y fallos del ciclo. El navegador estático solo sirve archivos públicos y fuentes de Google: no inicia Calendar, no manda formularios y no prueba la reserva real. La revisión estética no sustituye la prueba funcional ni una auditoría completa de accesibilidad.

En el entorno aislado de Codex para esta entrega, macOS impidió iniciar Chromium desde la terminal (`bootstrap_check_in: Permission denied`). Por tanto, la captura automática completa requiere su prueba en terminal local. La inspección visual de Dima se realizó con el navegador integrado; no equivale a una ejecución completa de Playwright.

Referencias de implementación: [capturas con Playwright](https://playwright.dev/python/docs/screenshots), [imágenes en la API de OpenAI](https://developers.openai.com/api/docs/guides/images-vision).
