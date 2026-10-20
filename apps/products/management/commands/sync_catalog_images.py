"""Upload repository product images to Cloudinary without replacing existing assets."""
from pathlib import Path

import cloudinary
from cloudinary import api, uploader
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Sincroniza las imágenes existentes del catálogo a Cloudinary solo si faltan."

    def handle(self, *args, **options):
        if not settings.CLOUDINARY_URL:
            raise CommandError("Configura CLOUDINARY_URL antes de sincronizar las imágenes.")
        cloudinary.config(secure=True)
        image_root = Path(settings.MEDIA_ROOT) / "products" / "img"
        if not image_root.is_dir():
            raise CommandError(f"No existe la carpeta de imágenes del catálogo: {image_root}")

        uploaded = 0
        preserved = 0
        for image_path in sorted(image_root.rglob("*")):
            if not image_path.is_file():
                continue
            public_id = image_path.relative_to(settings.MEDIA_ROOT).with_suffix("").as_posix()
            try:
                api.resource(public_id, resource_type="image")
            except cloudinary.exceptions.NotFound:
                uploader.upload(
                    str(image_path),
                    public_id=public_id,
                    overwrite=False,
                    resource_type="image",
                    unique_filename=False,
                    use_filename=False,
                )
                uploaded += 1
            except cloudinary.exceptions.Error as exc:
                raise CommandError(f"Cloudinary no pudo consultar {public_id}: {exc}") from exc
            else:
                preserved += 1

        self.stdout.write(self.style.SUCCESS(
            f"Imágenes sincronizadas: {uploaded} nuevas; {preserved} existentes se conservaron."
        ))
