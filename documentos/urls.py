from django.urls import path
from . import views

app_name = "documentos"

urlpatterns = [
    # Documentos
    path("", views.documento_list, name="documento_list"),
    path("nuevo/", views.documento_create, name="documento_create"),
    path("<int:doc_id>/editar/", views.documento_edit, name="documento_edit"),

    
    # Tipos de documento
    path("tipos/", views.tipo_documento_list, name="tipo_documento_list"),
    path("tipos/nuevo/", views.tipo_documento_create, name="tipo_documento_create"),

    # Etapas procesales
    path("etapas/", views.etapa_procesal_list, name="etapa_procesal_list"),
    path("etapas/nuevo/", views.etapa_procesal_create, name="etapa_procesal_create"),

    # Versiones
    path("<int:doc_id>/versiones/", views.version_list, name="version_list"),
    path("<int:doc_id>/versiones/nueva/", views.version_create, name="version_create"),
    
    #Navegación por carpetas
    path("carpeta/", views.carpeta_detalle, name="carpeta_raiz"),
    path("carpeta/<int:carpeta_id>/", views.carpeta_detalle, name="carpeta_detalle"),

]
