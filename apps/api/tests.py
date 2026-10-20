from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from apps.products.models import Category, Product, ProductSize


class CatalogApiTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name="Camisetas", slug="camisetas", icon="👕", order=1
        )
        self.product = Product.objects.create(
            name="Camiseta Colombia", sku="API-COL-01", description="Camiseta de prueba",
            price=Decimal("125000.00"), category=self.category, is_active=True,
            is_featured=True,
        )
        ProductSize.objects.create(product=self.product, size="M", stock=7)

    def test_versioned_categories_include_active_product_count(self):
        response = self.client.get(reverse("api:categories-v1"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["results"], [
            {"name": "Camisetas", "slug": "camisetas", "count": 1}
        ])

    def test_versioned_product_list_supports_search_and_category(self):
        response = self.client.get(
            reverse("api:products-v1"), {"q": "Colombia", "categoria": "camisetas"}
        )

        self.assertEqual(response.status_code, 200)
        result = response.json()["results"][0]
        self.assertEqual(response.json()["count"], 1)
        self.assertEqual(result["sku"], "API-COL-01")
        self.assertEqual(result["price"], "125000.00")
        self.assertEqual(result["currency"], "COP")
        self.assertEqual(result["stock"], 7)

    def test_versioned_product_detail_includes_sizes_and_returns_json_404(self):
        response = self.client.get(
            reverse("api:product-detail-v1", kwargs={"slug": self.product.slug})
        )
        missing = self.client.get(
            reverse("api:product-detail-v1", kwargs={"slug": "no-existe"})
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["product"]["sizes"], [
            {"id": self.product.sizes.get().pk, "size": "M", "stock": 7}
        ])
        self.assertEqual(missing.status_code, 404)
        self.assertEqual(missing.json()["code"], "not_found")
