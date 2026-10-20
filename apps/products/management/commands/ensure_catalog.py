"""Load the public starter catalog once into an empty deployment database."""
from django.core.management import call_command
from django.core.management.base import BaseCommand

from apps.products.models import Category, Product


class Command(BaseCommand):
    help = "Carga solo el catálogo público inicial si la base de datos aún está vacía."

    def handle(self, *args, **options):
        if Category.objects.exists() or Product.objects.exists():
            self.stdout.write("La base ya contiene categorías o productos; no se modificó el catálogo.")
            return
        call_command("loaddata", "catalog", verbosity=0)
        self.stdout.write(self.style.SUCCESS("Catálogo inicial cargado."))
