from unittest.mock import patch

import cloudinary.exceptions
from django.core.files.base import ContentFile
from django.test import SimpleTestCase

from apps.products.storage import CloudinaryMediaStorage, cloudinary_public_id


class CloudinaryMediaStorageTests(SimpleTestCase):
    def test_public_id_preserves_folder_and_removes_extension(self):
        self.assertEqual(
            cloudinary_public_id("products/img/camiseta_colombia.jpg"),
            "products/img/camiseta_colombia",
        )

    @patch("apps.products.storage.uploader.upload")
    def test_save_returns_cloudinary_public_id_with_real_format(self, upload):
        upload.return_value = {"public_id": "products/img/nuevo", "format": "webp"}

        saved_name = CloudinaryMediaStorage()._save(
            "products/img/nuevo.jpg", ContentFile(b"image-bytes")
        )

        self.assertEqual(saved_name, "products/img/nuevo.webp")
        self.assertEqual(upload.call_args.kwargs["public_id"], "products/img/nuevo")

    @patch("apps.products.storage.cloudinary_url")
    def test_url_is_generated_from_the_same_catalog_path(self, build_url):
        build_url.return_value = ("https://images.example/product.jpg", {})

        result = CloudinaryMediaStorage().url("products/img/product.jpg")

        self.assertEqual(result, "https://images.example/product.jpg")
        self.assertEqual(build_url.call_args.args[0], "products/img/product")

    @patch("apps.products.storage.api.resource", side_effect=cloudinary.exceptions.NotFound("missing"))
    def test_exists_returns_false_when_cloudinary_does_not_have_asset(self, resource):
        self.assertFalse(CloudinaryMediaStorage().exists("products/img/missing.jpg"))
        resource.assert_called_once_with("products/img/missing", resource_type="image")
