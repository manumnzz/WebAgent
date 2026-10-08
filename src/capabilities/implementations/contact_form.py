from capabilities.capability_implementation import (
    CapabilityImplementation,
)


def build_contact_form_implementation(
    contact_destination: str,
) -> CapabilityImplementation:

    clean_destination = contact_destination.strip()

    if not clean_destination:
        raise ValueError(
            "El destino del formulario de contacto no es válido."
        )

    html = f"""
<form
    class="capability-contact-form"
    action="mailto:{clean_destination}"
    method="post"
    enctype="text/plain"
>
    <div>
        <label for="contact-name">
            Nombre
        </label>

        <input
            type="text"
            id="contact-name"
            name="name"
            required
        >
    </div>

    <div>
        <label for="contact-email">
            Email
        </label>

        <input
            type="email"
            id="contact-email"
            name="email"
            required
        >
    </div>

    <div>
        <label for="contact-message">
            Mensaje
        </label>

        <textarea
            id="contact-message"
            name="message"
            required
        ></textarea>
    </div>

    <button type="submit">
        Enviar mensaje
    </button>
</form>
""".strip()

    return CapabilityImplementation(
        type="contact_form",
        html=html,
        css="",
        javascript="",
        implementation_notes=[
            "Formulario de contacto integrado mediante mailto."
        ],
    )