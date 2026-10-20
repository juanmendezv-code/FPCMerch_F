import logging
from decimal import Decimal
import requests
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

def usd_estimate(cop_price):
    rate = cache.get("usd_cop_rate")
    if rate is None:
        try:
            response = requests.get(settings.EXTERNAL_RATE_URL, timeout=3)
            response.raise_for_status()
            payload = response.json()
            rate = Decimal(str(payload["rates"]["COP"]))
            if rate <= 0: raise ValueError("Invalid exchange rate")
            cache.set("usd_cop_rate", rate, 21600)
        except (requests.RequestException, ValueError, KeyError, TypeError) as exc:
            logger.warning("No se pudo actualizar la tasa USD/COP: %s", exc)
            return None
    return (Decimal(str(cop_price)) / rate).quantize(Decimal("0.01"))
