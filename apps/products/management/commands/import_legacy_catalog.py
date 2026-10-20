import sqlite3
from decimal import Decimal, InvalidOperation
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connections, transaction
from django.utils.text import slugify

from apps.products.models import Category, Product, ProductSize


class Command(BaseCommand):
    help = "Importa categorías, productos y existencias desde las tablas SQLite heredadas."

    def handle(self, *args, **options):
        database_path = Path(connections["default"].settings_dict["NAME"]).resolve()
        if not database_path.is_file():
            raise CommandError(f"No existe la base de datos configurada: {database_path}")

        try:
            source = sqlite3.connect(database_path)
            source.row_factory = sqlite3.Row
            tables = {
                row[0]
                for row in source.execute("SELECT name FROM sqlite_master WHERE type='table'")
            }
            required_tables = {"categorias", "productos", "producto_tallas"}
            missing_tables = required_tables - tables
            if missing_tables:
                raise CommandError(
                    "No se encontraron las tablas de catálogo requeridas en "
                    f"{database_path.name}: {', '.join(sorted(missing_tables))}."
                )

            categories = source.execute("SELECT * FROM categorias ORDER BY id").fetchall()
            products = source.execute("SELECT * FROM productos ORDER BY id").fetchall()
            sizes = source.execute("SELECT * FROM producto_tallas ORDER BY id").fetchall()
        except sqlite3.Error as error:
            raise CommandError(f"No se pudo leer {database_path.name}: {error}") from error
        finally:
            if "source" in locals():
                source.close()

        categories_by_legacy_id = {}
        imported_products_by_legacy_id = {}
        imported_categories = 0
        imported_products = 0
        imported_sizes = 0
        skipped_products = 0
        missing_images = 0

        with transaction.atomic():
            for row in categories:
                name = (row["nombre"] or "").strip()
                if not name:
                    continue
                slug = (row["slug"] or slugify(name)).strip()[:50]
                if not slug:
                    slug = f"categoria-{row['id']}"
                category, created = Category.objects.update_or_create(
                    slug=slug,
                    defaults={
                        "name": name[:80],
                        "icon": (row["emoji"] or "⚽")[:40],
                        "order": max(0, int(row["id"])),
                    },
                )
                categories_by_legacy_id[int(row["id"])] = category
                imported_categories += int(created)

            for row in products:
                category = categories_by_legacy_id.get(int(row["categoria_id"]))
                name = (row["nombre"] or "").strip()
                if category is None or not name:
                    skipped_products += 1
                    continue
                try:
                    price = Decimal(str(row["precio"])).quantize(Decimal("0.01"))
                except (InvalidOperation, TypeError, ValueError) as error:
                    raise CommandError(
                        f"Precio no válido para el producto heredado {row['id']}."
                    ) from error
                if price < 0:
                    raise CommandError(f"El producto heredado {row['id']} tiene precio negativo.")

                legacy_id = int(row["id"])
                defaults = {
                    "name": name[:180],
                    "description": (row["descripcion"] or "").strip(),
                    "price": price,
                    "category": category,
                    "is_active": bool(row["activo"]),
                    "is_featured": bool(row["es_nuevo"]),
                }
                legacy_image = (row["imagen"] or "").strip().replace("\\", "/")
                if legacy_image:
                    media_root = settings.MEDIA_ROOT.resolve()
                    image_candidates = (
                        (media_root / legacy_image).resolve(),
                        (media_root / "products" / legacy_image).resolve(),
                    )
                    media_image = next(
                        (
                            candidate
                            for candidate in image_candidates
                            if candidate.is_file() and candidate.is_relative_to(media_root)
                        ),
                        None,
                    )
                    if media_image:
                        defaults["image"] = media_image.relative_to(media_root).as_posix()
                    else:
                        missing_images += 1

                product, created = Product.objects.update_or_create(
                    sku=f"LEGACY-{legacy_id:05d}", defaults=defaults
                )
                imported_products_by_legacy_id[legacy_id] = product
                imported_products += int(created)

            for row in sizes:
                product = imported_products_by_legacy_id.get(int(row["producto_id"]))
                size = (row["talla"] or "").strip()
                stock = int(row["stock"])
                if product is None or not size or len(size) > 12 or stock < 0:
                    continue
                _, created = ProductSize.objects.update_or_create(
                    product=product,
                    size=size,
                    defaults={"stock": stock},
                )
                imported_sizes += int(created)

        self.stdout.write(
            self.style.SUCCESS(
                "Catálogo importado desde "
                f"{database_path.name}: {imported_categories} categorías nuevas, "
                f"{imported_products} productos nuevos y {imported_sizes} tallas nuevas."
            )
        )
        if skipped_products:
            self.stdout.write(self.style.WARNING(f"Productos omitidos: {skipped_products}."))
        if missing_images:
            self.stdout.write(
                self.style.WARNING(
                    f"Imágenes no encontradas en media/: {missing_images}; "
                    "los productos usarán la imagen de respaldo hasta que cargues sus archivos."
                )
            )
        self.stdout.write(
            "La importación se puede repetir: actualizará las fichas importadas sin borrar "
            "productos ni tablas heredadas."
        )
