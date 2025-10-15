from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Bitacora, DetalleBitacora
# Create your views here.

@login_required
def bitacora_list(request):
    # Permite filtrar por usuario, acción o fecha
    usuario = request.GET.get("usuario")
    accion = request.GET.get("accion")
    fecha = request.GET.get("fecha")

    bitacoras = Bitacora.objects.select_related("idUsuario").order_by("-fecha")

    if usuario:
        bitacoras = bitacoras.filter(idUsuario__username__icontains=usuario)
    if accion:
        bitacoras = bitacoras.filter(login__icontains=accion)
    if fecha:
        bitacoras = bitacoras.filter(fecha__date=fecha)

    return render(request, "seguridad/bitacora_list.html", {"bitacoras": bitacoras})


#DETALLE DE LAS BITACORAS

@login_required
def bitacora_detalle(request, pk):
    bitacora = Bitacora.objects.get(pk=pk)
    detalles = DetalleBitacora.objects.filter(idBitacora=bitacora).order_by("-fecha")
    return render(request, "seguridad/bitacora_detalle.html", {"bitacora": bitacora, "detalles": detalles})
