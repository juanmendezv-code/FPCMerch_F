from .services import cart_data

def cart_summary(request):
    try: return {"cart_summary": cart_data(request)}
    except Exception: return {"cart_summary": {"count": 0, "total": 0, "lines": []}}
