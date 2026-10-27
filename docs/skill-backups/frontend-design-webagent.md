---
name: frontend-design
description: Diseñar e implementar webs de negocios con identidad visual propia, composición cuidada, tipografía expresiva, imágenes reales, movimiento selectivo y comportamiento responsive.
---

# Diseño visual de WebAgent

## Responsabilidad según el agente

Como DesignAgent:
- Definir la dirección visual antes de implementar.
- Expresar las decisiones mediante el schema de diseño disponible.
- No escribir HTML, CSS ni JavaScript.

Como DeveloperAgent:
- Ejecutar la dirección visual de WebsiteSpec.
- Resolver los detalles de implementación necesarios para materializarla.
- Conservar el contenido, la estructura y los contratos funcionales.

En modo repair:
- Corregir los errores indicados.
- Conservar la dirección visual y el comportamiento existente.
- Evitar un rediseño completo durante una reparación técnica.

## Identidad del negocio

Elegir una dirección visual que responda al negocio concreto:
su actividad, público, objetivo, preferencias y recursos disponibles.

Describir una idea visual reconocible y explicar qué decisiones
de composición, tipografía y color la materializan.

Distinguir preferencias estéticas de hechos del negocio.
No inventar antigüedad, premios, cifras, clientes ni garantías.

Respetar las preferencias explícitas del cliente.
Evitar aplicar automáticamente la misma estética a todos los sectores.

## Composición y ritmo

Definir la jerarquía de la primera pantalla:
mensaje principal, recurso visual y acción prioritaria.

Dar una función clara a cada sección.
Variar la composición cuando cambie el tipo de contenido:
presentación, servicios, galería, ubicación y contacto.

Utilizar alineaciones, proporciones y espacios coherentes.
Alternar densidad y espacio de descanso con intención.

Reservar las tarjetas para contenido que realmente forme unidades.
Evitar convertir todas las secciones en rejillas de tarjetas idénticas.

Utilizar bordes, sombras, numeración y elementos decorativos
cuando contribuyan a la lectura o a la identidad.

No añadir números que sugieran una secuencia si el contenido
no representa pasos o un orden real.

## Tipografía

Elegir una o dos familias con funciones claras.
Definir jerarquía de títulos, cuerpo y texto auxiliar.

Especificar familias concretas y alternativas de sistema.
Si se utiliza una fuente web, cargarla explícitamente.

Ajustar tamaño, peso, interlineado y longitud de línea
según el papel del texto.

Adaptar los títulos al espacio disponible sin recortes.
Evitar saltos de línea rígidos que rompan la composición móvil.

Mantener legibles los textos secundarios.
No utilizar tamaños diminutos para encajar contenido.

## Color y superficies

Definir colores por función:
fondo, superficie, texto, texto secundario, acento y borde.

Mantener contraste legible en todos los estados:
normal, hover, focus, seleccionado y deshabilitado.

Comprobar especialmente:
texto sobre fotografías, botones, campos y mensajes.

Reservar el acento para los elementos que necesitan prioridad.
Evitar que todos los componentes compitan visualmente.

Mantener coherencia con booking-theme.css cuando exista Booking.

## Recursos visuales

Utilizar las rutas de available_media.
Integrar el logo sin deformarlo ni recortarlo.

Elegir proporciones y tratamiento visual adecuados para cada imagen.
Conservar una presentación natural de las fotografías.

No deducir el contenido de una imagen únicamente por su nombre.
Los metadatos no equivalen a haber visto la fotografía.

No inventar fotografías, testimonios ni marcas de clientes.
No presentar una decoración como un mapa geográfico real.

Cuando falten recursos, resolver la composición con los disponibles
y registrar las limitaciones en los campos internos correspondientes.

## Movimiento

Diseñar una secuencia de entrada breve para los elementos principales
cuando encaje con la identidad del negocio.

Seleccionar algunos elementos para revelado al entrar en pantalla.
Evitar animar todos los párrafos y todas las tarjetas por defecto.

Utilizar transiciones que expliquen estados e interacciones.
Preferir transform y opacity para movimientos sencillos.

Evitar desplazamientos grandes, bucles decorativos constantes,
scroll secuestrado y efectos que dificulten leer o pulsar.

Respetar prefers-reduced-motion tanto en CSS como en JavaScript.

El contenido debe ser visible si JavaScript falla o está desactivado.
No ocultar inicialmente toda la página esperando una animación.

No retrasar el acceso a navegación, contacto o reservas.

## Adaptación móvil

Diseñar la composición móvil, no limitarse a reducir tamaños.

Definir el orden de lectura y cómo se reorganizan las columnas.
Mantener accesibles la navegación y la acción principal.

Si se oculta el menú de escritorio, proporcionar una alternativa
móvil operativa con controles accesibles.

Evitar desbordamientos horizontales, elementos superpuestos,
imágenes deformadas y botones difíciles de pulsar.

Si existe navegación fija, evitar que tape destinos de anclas,
campos o controles.

## Accesibilidad e implementación

Utilizar HTML semántico y controles nativos.
Proporcionar foco visible y navegación por teclado.

No depender exclusivamente de hover para acciones esenciales.
Dar nombres accesibles a los controles que solo muestran iconos.

Definir dimensiones o proporciones de imágenes para reducir
saltos de contenido durante la carga.

No cargar diferidamente la imagen principal si es esencial
para la primera pantalla.

Mantener las webs static-first.
Añadir dependencias únicamente si el comportamiento lo justifica.

## Integración de capabilities

Conservar URLs, identificadores, clases funcionales,
formularios y comportamiento de las implementaciones preconstruidas.

Respetar readiness, max_instances y allowed_zones.

Adaptar la presentación de las capabilities al diseño general.
Mantener reconocibles y utilizables sus acciones.

No inventar datos ni activar funcionalidades incompletas
para completar una composición visual.

## Antes de terminar

Revisar:
- Coherencia entre identidad, composición y tipografía.
- Claridad de la primera pantalla.
- Ritmo entre secciones.
- Uso correcto del logo y las imágenes disponibles.
- Legibilidad y estados interactivos.
- Navegación y acciones esenciales en móvil.
- Movimiento reducido y contenido accesible sin JavaScript.
- Conservación de las capabilities.

No afirmar que se han comprobado capturas, dispositivos,
contraste calculado o interacciones si esas pruebas no se ejecutaron.