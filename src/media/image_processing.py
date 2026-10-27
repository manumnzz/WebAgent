from io import BytesIO

from PIL import Image, ImageOps, UnidentifiedImageError

from media.models import MediaAsset, MediaRole



MAX_UPLOAD_BYTES = 10 * 1024 * 1024
MAX_IMAGE_PIXELS = 20_000_000
MAX_OUTPUT_DIMENSION = 2400

ALLOWED_INPUT_FORMATS = {"JPEG", "PNG", "WEBP"}


class InvalidMediaError(ValueError):
    pass

def prepare_image(
        content: bytes,
        *,
        role: MediaRole,
        alt_text: str | None = None,
) -> tuple[MediaAsset, bytes]:
    if not content:
        raise InvalidMediaError(
            "El archivo está vacío."
        )

    if len(content) > MAX_UPLOAD_BYTES:
        raise InvalidMediaError(
            "La imagen supera el máximo de 10 MiB."
        )

    try:
        with Image.open(BytesIO(content)) as image:
            if image.format not in ALLOWED_INPUT_FORMATS:
                raise InvalidMediaError(
                    "Solo se admiten imágenes JEPG, PNG, WebP."
                )

            if image.width * image.height > MAX_IMAGE_PIXELS:
                raise InvalidMediaError(
                    "La imagen supera el máximo de píxeles permitido."
                )

            if getattr(image, "is_animated", False):
                raise InvalidMediaError(
                    "No se admiten imágenes animadas."
                )

            image.load()

            oriented_image = ImageOps.exif_transpose(image)

            normalized_image = oriented_image.convert("RGBA")

            normalized_image.thumbnail(
                (
                    MAX_OUTPUT_DIMENSION,
                    MAX_OUTPUT_DIMENSION,
                ),
                Image.Resampling.LANCZOS,
            )

            #Conservar los píxeles sin copiar metadatos del archivo.
            clean_image = Image.new(
                "RGBA",
                normalized_image.size,
            )
            clean_image.paste(normalized_image)

            output = BytesIO()

            clean_image.save(
                output,
                format="WEBP",
                quality=85,
                method=4, 
            )

            prepared_content = output.getvalue()
            width, height = clean_image.size

    except InvalidMediaError:
        raise 

    except (
        UnidentifiedImageError,
        OSError,
        SyntaxError,
        ValueError,
        Image.DecompressionBombError,
    ) as error:
        raise InvalidMediaError (
            "No se ha podido leer una imágen válida."
        ) from error

    if len(prepared_content) > MAX_UPLOAD_BYTES:
        raise InvalidMediaError(
            "La imagen procesada supera el tamaño permitido."
        )

    asset = MediaAsset(
        role=role,
        format="webp",
        width=width,
        height=height,
        size_bytes=len(prepared_content),
        alt_text=alt_text,
    )

    return asset, prepared_content