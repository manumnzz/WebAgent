from capabilities.implementations.contact_form import (
    build_contact_form_implementation,
)

import pytest


def test_contact_form_capability():

    implementation = build_contact_form_implementation(
        contact_destination="contacto@irongarage.es"
    )

    assert implementation.type == "contact_form"

    assert (
        'action="mailto:contacto@irongarage.es"'
        in implementation.html
    )

    assert 'method="post"' in implementation.html

    assert 'type="email"' in implementation.html

    assert 'name="message"' in implementation.html

    assert "required" in implementation.html



def test_contact_form_rejects_empty_destination():

    with pytest.raises(ValueError):

        build_contact_form_implementation(
            contact_destination="   "
        )