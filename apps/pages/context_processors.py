from django.conf import settings

def store_info(request):
    return {"store_info": settings.STORE_INFO}
