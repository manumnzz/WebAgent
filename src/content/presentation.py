from pathlib import Path
from shutil import copyfile


RUNTIME_NAME = "website-content.js"
RUNTIME_PATH = Path(__file__).with_name(RUNTIME_NAME)

CONTENT_CONTRACT = """
WEBSITE_CONTENT_RUNTIME:
WebAgent publica content.json y website-content.js en la raíz de la web.
Carga <script src="website-content.js" defer></script> en index.html.
El script de WebAgent carga los datos. Conserva los marcadores HTML al
reparar la web y usa tu CSS para adaptar su diseño. No recrees el script,
no escribas content.json ni copies sus datos como valores fijos en HTML/JS.

Incluye estos contenedores aunque inicialmente estén vacíos. El atributo
hidden se retira por el script al cargar datos. Respeta [hidden] en CSS.
Adapta etiquetas y clases al diseño respetando los atributos del ejemplo.
El contenido repetido vive en un único template hijo directo de cada lista.

<div data-content-list="services" hidden>
  <template data-content-item>
    <article>
      <h3 data-content-field="name"></h3>
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

Deja un marcador para cada dato de contacto, aunque esté vacío al generar,
para que pueda publicarse después. Usa data-content-text="phone",
"whatsapp", "email" o "address" en elementos de texto inicialmente vacíos.
Si un dato tiene enlace equivalente, puedes usar ese enlace como marcador.
Para enlaces usa data-content-link="tel", "email", "whatsapp" o "maps"
en un <a hidden> sin href inicial. Para el formulario mailto usa el
fragmento oficial, con data-content-link="email" y sin action inicial.
Para Maps conserva el iframe con data-content-map y el enlace del fragmento
oficial. Ambos cargan la dirección desde content.json.
Usa data-content-text="business_name" si muestras el nombre como dato
independiente. Los eslóganes, titulares y el resto del copy editorial
proceden de WebsiteSpec.

Para la galería seleccionada usa el fragmento oficial. Si está seleccionada
y todavía no tiene imágenes, conserva su contenedor con hidden y su
template para mostrar imágenes cuando se añadan a content.json.
La ruta /reservar y sus opciones pertenecen a Booking.
"""


def install_content_runtime(website_root: Path) -> None:
    copyfile(RUNTIME_PATH, website_root / RUNTIME_NAME)
