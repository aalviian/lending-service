from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("billing/", include("billing.urls")),
    path("admin/", admin.site.urls),
]