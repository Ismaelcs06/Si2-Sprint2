from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.urls import reverse
from django.http import HttpResponse

from seguridad.models import Usuario, Rol, UsuarioRol
from actores.models import Actor
from .forms import (
    UserCreateForm, RoleForm, RoleAssignForm,
    ActorForm, AbogadoForm, ClienteForm, AsistenteForm
)

# ========================
# USUARIOS
# ========================
def users_list(request):
    q = request.GET.get("q", "").strip()
    users = Usuario.objects.all().order_by("-date_joined")

    if q:
        users = users.filter(username__icontains=q) | users.filter(email__icontains=q)

    return render(request, "accounts/users_list.html", {"users": users, "q": q})


def user_create(request):
    if request.method == "POST":
        form = UserCreateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Usuario creado correctamente.")
            return redirect("accounts:user_list")
    else:
        form = UserCreateForm()
    return render(request, "accounts/user_form.html", {"form": form})


# ========================
# ROLES
# ========================
def roles_list(request):
    roles = Rol.objects.all().order_by("nombre")
    return render(request, "accounts/roles_list.html", {"roles": roles})


def role_create(request):
    if request.method == "POST":
        form = RoleForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Rol creado correctamente.")
            return redirect("accounts:roles_list")
    else:
        form = RoleForm()
    return render(request, "accounts/role_form.html", {"form": form})


@transaction.atomic
def assign_roles(request, user_id):
    usuario = get_object_or_404(Usuario, pk=user_id)
    if request.method == "POST":
        form = RoleAssignForm(request.POST, usuario=usuario)
        if form.is_valid():
            nuevos = set(form.cleaned_data["roles"])
            actuales = set(Rol.objects.filter(usuariorol__usuario=usuario))

            # Añadir roles nuevos
            for r in nuevos - actuales:
                UsuarioRol.objects.create(usuario=usuario, rol=r, fechaAsignacion=None)

            # Eliminar roles removidos
            UsuarioRol.objects.filter(usuario=usuario, rol__in=(actuales - nuevos)).delete()

            messages.success(request, "Roles actualizados correctamente.")
            return redirect("accounts:user_list")
    else:
        form = RoleAssignForm(usuario=usuario)

    return render(request, "accounts/assign_roles.html", {"form": form, "usuario": usuario})


# ========================
# ACTORES
# ========================
def actor_create(request, user_id):
    usuario = get_object_or_404(Usuario, pk=user_id)

    if hasattr(usuario, "actor"):
        messages.warning(request, "Este usuario ya tiene un actor asociado.")
        return redirect("accounts:user_list")

    if request.method == "POST":
        form = ActorForm(request.POST)
        if form.is_valid():
            actor = form.save(commit=False)
            actor.usuario = usuario
            actor.creado_por = request.user  # 👈 auditoría
            actor.save()

            messages.success(request, f"Actor creado: {actor.tipoActor} para {usuario.username}.")
            if actor.tipoActor.upper() == "ABO":
                return redirect("accounts:abogado_create", actor_id=actor.id)
            elif actor.tipoActor.upper() == "CLI":
                return redirect("accounts:cliente_create", actor_id=actor.id)
            elif actor.tipoActor.upper() == "ASI":
                return redirect("accounts:asistente_create", actor_id=actor.id)

            return redirect("accounts:user_list")
    else:
        form = ActorForm()

    return render(request, "accounts/actor_form.html", {"form": form, "usuario": usuario})


def actors_list(request):
    tipo = request.GET.get("tipo", "").upper().strip()
    actores = Actor.objects.select_related("usuario").all().order_by("tipoActor", "nombres")

    if tipo in ["ABO", "CLI", "ASI"]:
        actores = actores.filter(tipoActor=tipo)

    actores_data = []
    for actor in actores:
        info_completa = False
        enlace_completar = None

        if actor.tipoActor.upper() == "ABO":
            if hasattr(actor, "abogado"):
                info_completa = True
            else:
                enlace_completar = reverse("accounts:abogado_create", args=[actor.id])
        elif actor.tipoActor.upper() == "CLI":
            if hasattr(actor, "cliente"):
                info_completa = True
            else:
                enlace_completar = reverse("accounts:cliente_create", args=[actor.id])
        elif actor.tipoActor.upper() == "ASI":
            if hasattr(actor, "asistente"):
                info_completa = True
            else:
                enlace_completar = reverse("accounts:asistente_create", args=[actor.id])

        actores_data.append({
            "actor": actor,
            "info_completa": info_completa,
            "enlace_completar": enlace_completar,
        })

    return render(request, "accounts/actors_list.html", {"actores_data": actores_data, "tipo": tipo})


# ========================
# SUBTIPOS DE ACTORES
# ========================
def abogado_create(request, actor_id):
    actor = get_object_or_404(Actor, pk=actor_id)
    if hasattr(actor, "abogado"):
        messages.info(request, "Ya existe un registro de Abogado para este actor.")
        return redirect("accounts:actors_list")

    if request.method == "POST":
        form = AbogadoForm(request.POST)
        if form.is_valid():
            ab = form.save(commit=False)
            ab.actor = actor
            ab.creado_por = request.user  # 👈 auditoría
            ab.save()
            messages.success(request, "Datos de abogado guardados correctamente.")
            return redirect("accounts:actors_list")
    else:
        form = AbogadoForm()

    return render(request, "accounts/actor_detail_form.html", {"form": form, "actor": actor, "tipo": "Abogado"})


def cliente_create(request, actor_id):
    actor = get_object_or_404(Actor, pk=actor_id)
    if hasattr(actor, "cliente"):
        messages.info(request, "Ya existe un registro de Cliente para este actor.")
        return redirect("accounts:actors_list")

    if request.method == "POST":
        form = ClienteForm(request.POST)
        if form.is_valid():
            c = form.save(commit=False)
            c.actor = actor
            c.creado_por = request.user  # 👈 auditoría
            c.save()
            messages.success(request, "Datos de cliente guardados correctamente.")
            return redirect("accounts:actors_list")
    else:
        form = ClienteForm()

    return render(request, "accounts/actor_detail_form.html", {"form": form, "actor": actor, "tipo": "Cliente"})


def asistente_create(request, actor_id):
    actor = get_object_or_404(Actor, pk=actor_id)
    if hasattr(actor, "asistente"):
        messages.info(request, "Ya existe un registro de Asistente para este actor.")
        return redirect("accounts:actors_list")

    if request.method == "POST":
        form = AsistenteForm(request.POST)
        if form.is_valid():
            a = form.save(commit=False)
            a.actor = actor
            a.creado_por = request.user  # 👈 auditoría
            a.save()
            messages.success(request, "Datos de asistente guardados correctamente.")
            return redirect("accounts:actors_list")
    else:
        form = AsistenteForm()

    return render(request, "accounts/actor_detail_form.html", {"form": form, "actor": actor, "tipo": "Asistente"})
