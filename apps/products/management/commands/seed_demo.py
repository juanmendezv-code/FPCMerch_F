from io import BytesIO
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from django.conf import settings
from django.core.management.base import CommandError
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.products.models import Category, Product, ProductSize

CATEGORIES = [
    ("Camisetas", "camisetas", "👕", 24, (26, 145, 89)),
    ("Pantalones", "pantalones", "👖", 12, (42, 97, 163)),
    ("Chaquetas", "chaquetas", "🧥", 8, (32, 70, 120)),
    ("Uniformes", "uniformes", "⚽", 10, (230, 120, 30)),
    ("Medias", "medias", "🧦", 15, (116, 74, 162)),
    ("Accesorios", "accesorios", "🎒", 20, (205, 68, 80)),
]
SIZES = {"Camisetas": ("XS", "S", "M", "L", "XL", "XXL"), "Pantalones": ("S", "M", "L", "XL"), "Chaquetas": ("S", "M", "L", "XL"), "Uniformes": ("S", "M", "L", "XL"), "Medias": ("S", "M", "L"), "Accesorios": ("ÚNICA",)}
SINGULAR = {"Camisetas": "Camiseta", "Pantalones": "Pantalón", "Chaquetas": "Chaqueta", "Uniformes": "Uniforme", "Medias": "Media", "Accesorios": "Accesorio"}

class Command(BaseCommand):
    help = "Carga de forma repetible 89 productos ilustrativos y sus imágenes placeholder."

    def handle(self, *args, **options):
        products = []
        for order, (name, slug, icon, quantity, color) in enumerate(CATEGORIES, 1):
            category, _ = Category.objects.update_or_create(slug=slug, defaults={"name": name, "icon": icon, "order": order})
            image_path = self.create_image(slug, name, color)
            for number in range(1, quantity + 1):
                sku = f"DEMO-{slug.upper()}-{number:02d}"
                product, _ = Product.objects.update_or_create(sku=sku, defaults={
                    "name": f"{SINGULAR[name]} FPC {number:02d}",
                    "description": f"Producto de demostración de la categoría {name}. Sustituye esta ficha por la información comercial verificada.",
                    "price": 35000 + ((number * 7250) % 230000), "category": category,
                    "image": image_path, "is_active": True, "is_featured": number <= 4,
                })
                products.append(product)
                sizes = SIZES[name]
                for size_index, size in enumerate(sizes):
                    ProductSize.objects.update_or_create(product=product, size=size, defaults={"stock": 5 + ((number + size_index) % 18)})
                ProductSize.objects.filter(product=product).exclude(size__in=sizes).delete()
        Product.objects.filter(sku__startswith="DEMO-").exclude(pk__in=[p.pk for p in products]).delete()
        self.create_users()
        self.stdout.write(self.style.SUCCESS(f"Carga lista: {len(products)} productos en 6 categorías."))

    def create_image(self, slug, name, color):
        relative_path = f"products/demo/{slug}.png"
        if default_storage.exists(relative_path): return relative_path
        image = Image.new("RGB", (720, 720), (244, 247, 245))
        draw = ImageDraw.Draw(image)
        draw.rounded_rectangle((175, 150, 545, 570), radius=42, fill=color)
        draw.polygon([(235, 150), (315, 90), (405, 90), (485, 150), (430, 235), (430, 490), (290, 490), (290, 235)], fill=color)
        draw.text((230, 525), name.upper(), fill=(255, 255, 255), stroke_width=0)
        buffer = BytesIO(); image.save(buffer, format="PNG")
        default_storage.save(relative_path, ContentFile(buffer.getvalue()))
        return relative_path

    def create_users(self):
        User = get_user_model()
        user, created = User.objects.get_or_create(email="cliente@fpcmerch.test", defaults={"first_name": "Cliente", "last_name": "Demo", "ciudad": "Bogotá"})
        if created:
            customer_password = os.environ.get("FPCMERCH_DEMO_CUSTOMER_PASSWORD")
            if customer_password:
                user.set_password(customer_password)
            else:
                user.set_unusable_password()
            user.save()
        if settings.DEBUG and os.environ.get("FPCMERCH_CREATE_SUPERUSER") == "1":
            admin_password = os.environ.get("FPCMERCH_DEMO_SUPERUSER_PASSWORD")
            if not admin_password:
                raise CommandError(
                    "Define FPCMERCH_DEMO_SUPERUSER_PASSWORD en el entorno para "
                    "crear el superusuario de demostración."
                )
            admin, created = User.objects.get_or_create(email="admin@fpcmerch.test", defaults={"is_staff": True, "is_superuser": True, "first_name": "Admin", "last_name": "Demo"})
            if created:
                admin.set_password(admin_password)
                admin.save()
