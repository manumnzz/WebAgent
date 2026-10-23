# Booking V1: reservas, llegadas y consultas

Cada opción del encargo tiene uno de estos comportamientos:

| Modo | Datos del visitante | Google Calendar | Mensaje al visitante |
| --- | --- | --- | --- |
| Con duración | Día, hora, contacto y notas opcionales | Evento ocupado; puede invitar al cliente por email | Reserva confirmada |
| Llegada pendiente | Día, hora propuesta, contacto y motivo obligatorio | Evento privado y transparente, marcado `[PENDIENTE]`, sin invitación | Espera la confirmación del negocio antes de acudir |
| Consulta sin hora | Contacto y motivo obligatorio | Evento privado de todo el día, transparente y marcado `[CONSULTA PENDIENTE]` | El negocio responderá; no hay cita |

Una llegada pendiente ocupa visualmente un intervalo de `slot_interval_minutes` en Calendar, pero queda como disponible para `freeBusy`. Ese intervalo indica la separación entre horas ofrecidas, **no** la duración del trabajo ni la capacidad física del local. El negocio debe comprobar si tiene espacio, contactar al cliente y confirmar o proponer otra hora. En V1 esa decisión se hace manualmente en Calendar y por el canal de contacto que el cliente indicó; no existe un panel de aprobación ni una confirmación automática de la capacidad.

El formulario de encargo guarda `booking.appointment_modes` para las opciones sin duración. `pending_arrival` pide una hora propuesta; `inquiry` no pide hora. Los JSON antiguos sin este campo conservan su significado previo: una opción sin duración es una consulta, no se convierte silenciosamente en una llegada.

Al generar, WebAgent incorpora las tres clases de opción en `config/booking.json`. El servidor existente (`api.main:app`) sirve `/reservar` y los endpoints `/booking`, `/booking/requests` y `/booking/inquiries`. El evento solo se comunica como recibido cuando Google Calendar devuelve su identificador.

**Antes de usarlo públicamente:** configurar el calendario del negocio y sus credenciales en el servidor, asegurar una forma de atender las solicitudes pendientes y proteger los endpoints públicos contra envíos abusivos. La configuración de desarrollo usa un único `config/booking.json` compartido; generar otra web lo reemplaza, por lo que el despliegue de varios negocios necesita separar la configuración por sitio.
