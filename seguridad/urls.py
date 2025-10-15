from django.urls import path
from . import views

app_name = "seguridad"

urlpatterns = [
    path("bitacora/", views.bitacora_list, name="bitacora_list"),
    path("bitacora/<int:pk>/", views.bitacora_detalle, name="bitacora_detalle"),
]
