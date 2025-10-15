# accounts/urls.py
from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    #ruta para la vista de listado de usuarios
    path("users/", views.users_list, name="user_list"),  
    
    #ruta para la vista de creacion de usuarios
    path("users/create/", views.user_create, name="user_create"), 

    #ruta para la vista de creacion de actores
    path("users/<int:user_id>/actor/", views.actor_create, name="actor_create"),
    
    #ruta para la vista de listado de roles
    path("roles/", views.roles_list, name="roles_list"),
    
    #Ruta para la vista de creacion de roles
    path("roles/create/", views.role_create, name="role_create"),
    
    #ruta para la vista de asignacion de roles a usuarios
    path("users/<int:user_id>/roles/", views.assign_roles, name="assign_roles"),
    
    #Ruta para la vista de todos los actores
    path("actors/", views.actors_list, name="actors_list"),

    #Rutas para la creacion de las clases generalizadas: Abogado, Cliente, Asistente
    path("actors/<int:actor_id>/abogado/", views.abogado_create, name="abogado_create"),
    path("actors/<int:actor_id>/cliente/", views.cliente_create, name="cliente_create"),
    path("actors/<int:actor_id>/asistente/", views.asistente_create, name="asistente_create"),

    
]
