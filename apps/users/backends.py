from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        email = (kwargs.get("email") or username or "").strip().lower()
        if not email or password is None:
            return None
        try:
            user = get_user_model().objects.get(email__iexact=email)
        except get_user_model().DoesNotExist:
            user = get_user_model()()
            user.set_password(password)
            return None
        return user if user.check_password(password) and self.user_can_authenticate(user) else None
