"""Cloudinary-backed media storage used when CLOUDINARY_URL is configured."""
from pathlib import PurePosixPath

import cloudinary
import requests
from cloudinary import api, uploader
from cloudinary.utils import cloudinary_url
from django.core.files.base import ContentFile
from django.core.files.storage import Storage


def cloudinary_public_id(name):
    """Convert a Django media path to the matching Cloudinary public ID."""
    return PurePosixPath(str(name).replace("\\", "/")).with_suffix("").as_posix()


class CloudinaryMediaStorage(Storage):
    """Store uploaded product images in Cloudinary while keeping DB names portable."""

    def _open(self, name, mode="rb"):
        if mode not in {"rb", "r"}:
            raise ValueError("CloudinaryMediaStorage solo permite lectura.")
        response = requests.get(self.url(name), timeout=30)
        response.raise_for_status()
        return ContentFile(response.content, name=name)

    def _save(self, name, content):
        public_id = cloudinary_public_id(name)
        result = uploader.upload(
            content,
            public_id=public_id,
            overwrite=True,
            resource_type="image",
            unique_filename=False,
            use_filename=False,
        )
        extension = result.get("format") or PurePosixPath(name).suffix.lstrip(".")
        return f"{result['public_id']}.{extension}" if extension else result["public_id"]

    def delete(self, name):
        uploader.destroy(cloudinary_public_id(name), resource_type="image")

    def exists(self, name):
        try:
            api.resource(cloudinary_public_id(name), resource_type="image")
        except cloudinary.exceptions.NotFound:
            return False
        return True

    def size(self, name):
        return api.resource(cloudinary_public_id(name), resource_type="image")["bytes"]

    def url(self, name):
        return cloudinary_url(
            cloudinary_public_id(name), secure=True, resource_type="image"
        )[0]
