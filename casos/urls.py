from django.urls import path
from . import views

app_name = "casos"

urlpatterns = [
    path("", views.caso_list, name="case_list"),
    path("crear/", views.caso_create, name="case_create"),
    path("<int:pk>/editar/", views.caso_edit, name="case_edit"),
    
    
    # EquipoCaso
    path("<int:caso_id>/equipo/", views.equipo_caso_list, name="equipo_list"),
    path("<int:caso_id>/equipo/agregar/", views.equipo_caso_add, name="equipo_add"),

    # Parte Procesal
    path("<int:caso_id>/partes/", views.parte_procesal_list, name="parte_list"),
    path("<int:caso_id>/partes/agregar/", views.parte_procesal_add, name="parte_add"),
    
    
    # Expedientes
    path("expedientes/", views.expediente_list, name="expediente_list"),
    path("<int:caso_id>/expediente/crear/", views.expediente_create, name="expediente_create"),
    
    # Carpetas
    path("expedientes/<int:expediente_id>/carpetas/", views.carpeta_list, name="carpeta_list"),
    path("expedientes/<int:expediente_id>/carpetas/crear/", views.carpeta_create, name="carpeta_create"),
    
    path("carpetas/", views.carpeta_global_list, name="carpeta_global_list"),

    #TimeLine

    path('expediente/<int:expediente_id>/timeline/', views.expediente_timeline, name='expediente_timeline'),


]
