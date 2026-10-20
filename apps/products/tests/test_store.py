from decimal import Decimal
from unittest.mock import patch
import requests
from django.test import TestCase
from django.urls import reverse
from apps.api.external import usd_estimate
from apps.cart.models import Cart, CartItem
from apps.cart.services import CART_KEY, OutOfStockError
from apps.contact.models import ContactMessage
from apps.orders.models import Order, OrderItem
from apps.orders.services import create_order
from apps.products.models import Category, Product, ProductSize
from apps.users.models import User

class StoreTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="user@example.test", password="StrongPass2026!", first_name="Ana")
        self.category = Category.objects.create(name="Camisetas", slug="camisetas")
        self.product = Product.objects.create(name="Camiseta Local", sku="TEST-01", description="Prenda de prueba", price=Decimal("85000"), category=self.category)
        self.size = ProductSize.objects.create(product=self.product, size="M", stock=5)

    def test_cart_session_add_update_remove_and_stock_limit(self):
        response = self.client.post(reverse("api:cart-add"), data={"product_id": self.product.pk, "size_id": self.size.pk, "quantity": 2}, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], 2)
        over = self.client.post(reverse("api:cart-add"), data={"product_id": self.product.pk, "size_id": self.size.pk, "quantity": 9}, content_type="application/json")
        self.assertEqual(over.status_code, 400)
        self.assertEqual(over.json()["code"], "out_of_stock")
        self.client.post(reverse("api:cart-update"), data={"size_id": self.size.pk, "quantity": 3}, content_type="application/json")
        self.assertEqual(self.client.get(reverse("api:cart")).json()["count"], 3)
        self.client.post(reverse("api:cart-remove"), data={"size_id": self.size.pk}, content_type="application/json")
        self.assertEqual(self.client.get(reverse("api:cart")).json()["count"], 0)

    def test_login_uses_email_and_merges_session_cart(self):
        session = self.client.session
        session[CART_KEY] = {str(self.size.pk): 2}
        session.save()
        response = self.client.post(reverse("users:login"), {"email": self.user.email, "password": "StrongPass2026!", "remember": "on"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(CartItem.objects.get(cart__user=self.user, variant=self.size).quantity, 2)
        self.assertNotIn(CART_KEY, self.client.session)

    def test_checkout_decrements_stock_and_copies_price(self):
        self.client.force_login(self.user)
        cart, _ = Cart.objects.get_or_create(user=self.user)
        CartItem.objects.create(cart=cart, variant=self.size, quantity=2)
        request = self._request_with_session()
        order = create_order(request, {"shipping_address": "Calle 1 #2-3", "city": "Bogotá", "phone": "3000000000", "payment_method": "demo_card"})
        self.size.refresh_from_db()
        self.assertEqual(self.size.stock, 3)
        self.assertEqual(order.items.get().unit_price, Decimal("85000"))
        self.assertEqual(order.shipping_cost, Decimal("0"))
        self.assertFalse(CartItem.objects.filter(cart=cart).exists())

    def test_checkout_rolls_back_all_changes_on_simultaneous_stock_loss(self):
        second = Product.objects.create(name="Short Stock", sku="TEST-02", description="Prueba", price=Decimal("50000"), category=self.category)
        unavailable = ProductSize.objects.create(product=second, size="M", stock=0)
        cart, _ = Cart.objects.get_or_create(user=self.user)
        CartItem.objects.create(cart=cart, variant=self.size, quantity=2)
        CartItem.objects.create(cart=cart, variant=unavailable, quantity=1)
        request = self._request_with_session()
        with self.assertRaises(OutOfStockError):
            create_order(request, {"shipping_address": "Calle 1", "city": "Bogotá", "phone": "3000", "payment_method": "demo_card"})
        self.size.refresh_from_db()
        self.assertEqual(self.size.stock, 5)
        self.assertEqual(Order.objects.count(), 0)

    def test_owner_privacy_and_management_access(self):
        other = User.objects.create_user(email="other@example.test", password="StrongPass2026!")
        order = Order.objects.create(user=other, number="FPC-PRIVACY", shipping_address="Calle 1", city="Bogotá", phone="3000", subtotal=10, shipping_cost=0, total=10)
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(reverse("orders:detail", args=[order.number])).status_code, 404)
        self.client.logout()
        self.assertEqual(self.client.get(reverse("products:manage")).status_code, 302)
        staff = User.objects.create_user(email="staff@example.test", password="StrongPass2026!", is_staff=True)
        self.client.force_login(staff)
        self.assertEqual(self.client.get(reverse("products:manage")).status_code, 200)

    def test_delete_protected_product_deactivates_it(self):
        staff = User.objects.create_user(email="manager@example.test", password="StrongPass2026!", is_staff=True)
        order = Order.objects.create(user=self.user, number="FPC-KEEP", shipping_address="Calle 1", city="Bogotá", phone="3000", subtotal=85000, shipping_cost=0, total=85000)
        OrderItem.objects.create(order=order, product=self.product, size=self.size.size, quantity=1, unit_price=self.product.price)
        self.client.force_login(staff)
        response = self.client.post(reverse("products:delete", args=[self.product.pk]))
        self.assertEqual(response.status_code, 302)
        self.product.refresh_from_db()
        self.assertFalse(self.product.is_active)

    def test_contact_form_saves_only_valid_message(self):
        response = self.client.post(reverse("contact:contact"), {"name": "Ana", "email": "bad", "subject": "other", "message": "Hola"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ContactMessage.objects.count(), 0)
        success = self.client.post(reverse("contact:contact"), {"name": "Ana", "email": "ana@example.test", "subject": "other", "message": "Hola"})
        self.assertEqual(success.status_code, 302)
        self.assertEqual(ContactMessage.objects.count(), 1)
        followed = self.client.get(success.url)
        self.assertContains(followed, 'id="contactSuccess"')

    def test_json_api_list_and_external_rate_fallback(self):
        self.assertTrue(self.client.get(reverse("api:products")).json()["ok"])
        self.assertEqual(self.client.post(reverse("api:products")).status_code, 405)
        with patch("apps.api.external.requests.get", side_effect=requests.Timeout("offline")):
            self.assertIsNone(usd_estimate(Decimal("85000")))

    def test_store_pages_render(self):
        with patch("apps.products.views.usd_estimate", return_value=Decimal("26.58")):
            self.assertEqual(self.client.get(reverse("pages:home")).status_code, 200)
            self.assertEqual(self.client.get(reverse("products:catalog")).status_code, 200)
            self.assertEqual(self.client.get(reverse("products:detail", args=[self.product.slug])).status_code, 200)
        self.assertEqual(self.client.get(reverse("cart:view")).status_code, 200)
        self.assertEqual(self.client.get(reverse("pages:info", args=["terminos"])).status_code, 200)

    def test_registration_validates_and_creates_email_user(self):
        response = self.client.post(reverse("users:register"), {
            "first_name": "Luis", "last_name": "Pérez", "email": "luis@example.test",
            "password1": "StrongReg2026!", "password2": "StrongReg2026!", "accept_terms": "on",
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(email="luis@example.test").exists())
        self.assertNotEqual(User.objects.get(email="luis@example.test").password, "StrongReg2026!")

    def test_product_management_create_and_delete(self):
        staff = User.objects.create_user(email="staff@example.test", password="StrongPass2026!", is_staff=True)
        self.client.force_login(staff)
        created = self.client.post(reverse("products:create"), {
            "name": "Nueva camiseta", "sku": "CRUD-01", "description": "Descripción", "price": "50000", "category": self.category.pk, "is_active": "on",
            "sizes-TOTAL_FORMS": "1", "sizes-INITIAL_FORMS": "0", "sizes-MIN_NUM_FORMS": "0", "sizes-MAX_NUM_FORMS": "1000", "sizes-0-size": "L", "sizes-0-stock": "4",
        })
        self.assertEqual(created.status_code, 302)
        self.assertEqual(self.client.get(reverse("products:create")).status_code, 200)
        product = Product.objects.get(sku="CRUD-01")
        self.assertTrue(ProductSize.objects.filter(product=product, size="L", stock=4).exists())
        variant = ProductSize.objects.get(product=product, size="L")
        updated = self.client.post(reverse("products:update", args=[product.pk]), {
            "name": "Nueva camiseta editada", "sku": "CRUD-01", "description": "Descripción actualizada", "price": "62000", "category": self.category.pk, "is_active": "on",
            "sizes-TOTAL_FORMS": "4", "sizes-INITIAL_FORMS": "1", "sizes-MIN_NUM_FORMS": "0", "sizes-MAX_NUM_FORMS": "1000",
            "sizes-0-id": variant.pk, "sizes-0-product": product.pk, "sizes-0-size": "L", "sizes-0-stock": "7",
        })
        self.assertEqual(updated.status_code, 302)
        product.refresh_from_db(); variant.refresh_from_db()
        self.assertEqual(product.price, Decimal("62000"))
        self.assertEqual(variant.stock, 7)
        removed = self.client.post(reverse("products:delete", args=[product.pk]))
        self.assertEqual(removed.status_code, 302)
        self.assertFalse(Product.objects.filter(pk=product.pk).exists())

    def test_admin_price_edit_is_saved_and_visible_on_store_pages(self):
        admin_user = User.objects.create_superuser(email="admin@example.test", password="StrongPass2026!")
        self.client.force_login(admin_user)

        response = self.client.post(reverse("admin:products_product_change", args=[self.product.pk]), {
            "name": self.product.name,
            "slug": self.product.slug,
            "sku": self.product.sku,
            "description": self.product.description,
            "price": "92000.00",
            "category": self.category.pk,
            "is_active": "on",
            "is_featured": "on",
            "sizes-TOTAL_FORMS": "1",
            "sizes-INITIAL_FORMS": "1",
            "sizes-MIN_NUM_FORMS": "0",
            "sizes-MAX_NUM_FORMS": "1000",
            "sizes-0-id": self.size.pk,
            "sizes-0-product": self.product.pk,
            "sizes-0-size": self.size.size,
            "sizes-0-stock": self.size.stock,
            "_save": "Guardar",
        })
        self.assertEqual(response.status_code, 302, response.content.decode())

        self.product.refresh_from_db()
        self.assertEqual(self.product.price, Decimal("92000.00"))
        catalog = self.client.get(reverse("products:catalog"))
        detail = self.client.get(reverse("products:detail", args=[self.product.slug]))
        self.assertContains(catalog, "92.000")
        self.assertContains(detail, "92.000")

    def test_site_logout_requires_post_and_clears_session(self):
        from django.test import Client
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.force_login(self.user)

        profile = csrf_client.get(reverse("users:profile"))
        self.assertContains(profile, 'method="post"')
        self.assertContains(profile, 'name="csrfmiddlewaretoken"')
        csrf_token = csrf_client.cookies["csrftoken"].value

        get_response = csrf_client.get(reverse("users:logout"))
        self.assertEqual(get_response.status_code, 405)
        self.assertIn("_auth_user_id", csrf_client.session)

        post_response = csrf_client.post(reverse("users:logout"), HTTP_X_CSRFTOKEN=csrf_token)
        self.assertRedirects(post_response, reverse("pages:home"))
        self.assertNotIn("_auth_user_id", csrf_client.session)

        second_user = User.objects.create_user(email="second@example.test", password="OtherPass2026!")
        login_response = csrf_client.post(reverse("users:login"), {
            "email": second_user.email,
            "password": "OtherPass2026!",
            "remember": "on",
        }, HTTP_X_CSRFTOKEN=csrf_token)
        self.assertEqual(login_response.status_code, 302)
        self.assertEqual(csrf_client.session.get("_auth_user_id"), str(second_user.pk))

    def test_admin_logout_form_post_clears_session_and_get_is_not_allowed(self):
        from django.test import Client
        admin_user = User.objects.create_superuser(email="admin@example.test", password="StrongPass2026!")
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.force_login(admin_user)

        admin_index = csrf_client.get(reverse("admin:index"))
        self.assertContains(admin_index, 'id="logout-form"')
        self.assertContains(admin_index, 'name="csrfmiddlewaretoken"')
        csrf_token = csrf_client.cookies["csrftoken"].value

        get_response = csrf_client.get("/admin/logout/")
        self.assertEqual(get_response.status_code, 405)
        self.assertIn("_auth_user_id", csrf_client.session)

        post_response = csrf_client.post("/admin/logout/", HTTP_X_CSRFTOKEN=csrf_token)
        self.assertEqual(post_response.status_code, 302)
        self.assertNotIn("_auth_user_id", csrf_client.session)

        login_response = csrf_client.post(reverse("users:login"), {
            "email": self.user.email,
            "password": "StrongPass2026!",
            "remember": "on",
        }, HTTP_X_CSRFTOKEN=csrf_token)
        self.assertEqual(login_response.status_code, 302)
        self.assertEqual(csrf_client.session.get("_auth_user_id"), str(self.user.pk))

    def test_admin_can_logout_from_store_and_become_anonymous(self):
        admin_user = User.objects.create_superuser(email="admin@example.test", password="StrongPass2026!")
        self.client.force_login(admin_user)

        response = self.client.post(reverse("users:logout"))

        self.assertRedirects(response, reverse("pages:home"))
        self.assertNotIn("_auth_user_id", self.client.session)
        admin_response = self.client.get(reverse("admin:index"))
        self.assertRedirects(admin_response, "/admin/login/?next=/admin/")

    def test_account_order_and_password_reset_templates_render(self):
        self.assertEqual(self.client.get(reverse("users:login")).status_code, 200)
        self.assertEqual(self.client.get(reverse("users:register")).status_code, 200)
        self.assertEqual(self.client.get(reverse("password_reset")).status_code, 200)
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(reverse("users:profile")).status_code, 200)
        cart, _ = Cart.objects.get_or_create(user=self.user)
        CartItem.objects.create(cart=cart, variant=self.size, quantity=1)
        self.assertEqual(self.client.get(reverse("orders:checkout")).status_code, 200)
        self.client.logout()
        admin = User.objects.create_superuser(email="admin@example.test", password="StrongPass2026!")
        self.client.force_login(admin)
        self.assertEqual(self.client.get("/admin/users/user/add/").status_code, 200)

    def _request_with_session(self):
        from django.test import RequestFactory
        from django.contrib.sessions.middleware import SessionMiddleware
        request = RequestFactory().post("/checkout/")
        middleware = SessionMiddleware(lambda req: None); middleware.process_request(request); request.session.save()
        request.user = self.user
        return request
