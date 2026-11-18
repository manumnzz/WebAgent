from typing import Annotated
from urllib.parse import urlsplit

from pydantic import AfterValidator, BaseModel, Field


def validate_google_maps_url(value: str) -> str:
    url = urlsplit(value)
    host = url.hostname
    is_maps = (
        host in {"google.com", "www.google.com", "maps.google.com", "www.google.es"}
        and (url.path == "/maps" or url.path.startswith("/maps/"))
    )
    is_share_link = host in {"maps.app.goo.gl", "g.page"} and url.path not in {"", "/"}

    if (
        url.scheme != "https"
        or url.username is not None
        or url.password is not None
        or url.port is not None
        or not (is_maps or is_share_link)
        or any(character.isspace() or character == "\\" for character in value)
    ):
        raise ValueError("Se necesita un enlace HTTPS a la ficha de Google Maps.")
    return value


GoogleMapsURL = Annotated[str, AfterValidator(validate_google_maps_url)]


class ReviewData(BaseModel):
    author: str
    text: str
    rating: int = Field(ge=1, le=5)
    google_maps_url: GoogleMapsURL | None = None
