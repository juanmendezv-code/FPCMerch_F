from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.contrib.auth import views as auth_views

handler400 = "apps.pages.views.bad_request"
handler403 = "apps.pages.views.permission_denied"
handler404 = "apps.pages.views.page_not_found"
handler500 = "apps.pages.views.server_error"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.pages.urls")),
    path("", include("apps.products.urls")),
    path("", include("apps.users.urls")),
    path("", include("apps.cart.urls")),
    path("", include("apps.orders.urls")),
    path("", include("apps.contact.urls")),
    path("api/", include("apps.api.urls")),
    path("cuenta/recuperar/", auth_views.PasswordResetView.as_view(template_name="registration/password_reset_form.html", email_template_name="registration/password_reset_email.html", subject_template_name="registration/password_reset_subject.txt", success_url="/cuenta/recuperar/enviado/"), name="password_reset"),
    path("cuenta/recuperar/enviado/", auth_views.PasswordResetDoneView.as_view(template_name="registration/password_reset_done.html"), name="password_reset_done"),
    path("cuenta/recuperar/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(template_name="registration/password_reset_confirm.html", success_url="/cuenta/recuperar/completo/"), name="password_reset_confirm"),
    path("cuenta/recuperar/completo/", auth_views.PasswordResetCompleteView.as_view(template_name="registration/password_reset_complete.html"), name="password_reset_complete"),
    path("cuenta/", include("django.contrib.auth.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
