from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Documento, VersionDocumento, TipoDocumento, EtapaProcesal
from .forms import DocumentoForm, VersionDocumentoForm, TipoDocumentoForm, EtapaProcesalForm
from django.db.models import Max
from django.utils import timezone
from casos.models import Carpeta
# Create your views here.


# ======= DOCUMENTOS ======= #
def documento_list(request):
    documentos = Documento.objects.select_related("carpeta", "tipoDocumento").all()
    return render(request, "documentos/documento_list.html", {"documentos": documentos})


def documento_create(request):
    if request.method == "POST":
        form = DocumentoForm(request.POST, request.FILES)
        if form.is_valid():
            documento = form.save(commit=False)
            documento.creado_por = request.user  # registra usuario creador
            documento.save()

            # 🧾 Registrar evento en el timeline del expediente
            try:
                from casos.utils import registrar_evento_exp
                expediente = documento.carpeta.expediente
                registrar_evento_exp(
                    request.user,
                    expediente,
                    "DOCUMENTO",
                    f"Se registró el documento '{documento.nombreDocumento}'."
                )
            except Exception as e:
                print("⚠️ No se pudo registrar evento de documento:", e)

            messages.success(request, f"Documento '{documento.nombreDocumento}' registrado correctamente.")
            return redirect("documentos:documento_list")
    else:
        form = DocumentoForm()

    return render(request, "documentos/documento_form.html", {"form": form})


def documento_edit(request, doc_id):
    documento = get_object_or_404(Documento, pk=doc_id)
    if request.method == "POST":
        form = DocumentoForm(request.POST, request.FILES, instance=documento)
        if form.is_valid():
            documento = form.save(commit=False)
            documento.modificado_por = request.user  # 👈 registra quién lo editó
            documento.save()
            messages.success(request, "Documento actualizado correctamente.")
            return redirect("documentos:documento_list")
    else:
        form = DocumentoForm(instance=documento)
    return render(request, "documentos/documento_form.html", {"form": form, "documento": documento})


# ======= VERSIONES ======= #
def version_list(request, doc_id):
    documento = get_object_or_404(Documento, pk=doc_id)
    versiones = documento.versiones.select_related("creado_por").all()
    return render(request, "documentos/version_list.html", {"documento": documento, "versiones": versiones})


def version_create(request, doc_id):
    documento = get_object_or_404(Documento, pk=doc_id)

    if request.method == "POST":
        form = VersionDocumentoForm(request.POST, request.FILES)
        if form.is_valid():
            ultima = documento.versiones.aggregate(Max("numeroVersion"))["numeroVersion__max"] or 0
            nueva = form.save(commit=False)
            nueva.documento = documento
            nueva.creado_por = request.user
            nueva.numeroVersion = ultima + 1
            nueva.fechaCambio = timezone.now()
            nueva.save()

            # 🧾 Registrar evento en el timeline del expediente
            try:
                from casos.utils import registrar_evento_exp
                expediente = documento.carpeta.expediente
                registrar_evento_exp(
                    request.user,
                    expediente,
                    "VERSION",
                    f"Se creó la versión {nueva.numeroVersion} del documento '{documento.nombreDocumento}'."
                )
            except Exception as e:
                print("⚠️ No se pudo registrar evento de versión:", e)

            # (Opcional) Registrar en bitácora si la tienes activa
            try:
                from seguridad.signals import registrar_detalle
                registrar_detalle(
                    request.user,
                    "Nueva versión",
                    "VersionDocumento",
                    f"Versión {nueva.numeroVersion} creada para {documento.nombreDocumento}"
                )
            except Exception as e:
                print("⚠️ No se pudo registrar detalle de bitácora:", e)

            messages.success(request, f"Versión {nueva.numeroVersion} registrada correctamente.")
            return redirect("documentos:version_list", doc_id=documento.id)
    else:
        form = VersionDocumentoForm()

    return render(request, "documentos/version_form.html", {"form": form, "documento": documento})



# === TIPO DE DOCUMENTO ===

def tipo_documento_list(request):
    tipos = TipoDocumento.objects.all().order_by("nombre")
    return render(request, "documentos/tipo_documento_list.html", {"tipos": tipos})


def tipo_documento_create(request):
    if request.method == "POST":
        form = TipoDocumentoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Tipo de documento creado correctamente.")
            return redirect("documentos:tipo_documento_list")
    else:
        form = TipoDocumentoForm()
    return render(request, "documentos/tipo_documento_form.html", {"form": form})


# === ETAPA PROCESAL ===

def etapa_procesal_list(request):
    etapas = EtapaProcesal.objects.all().order_by("nombre")
    return render(request, "documentos/etapa_procesal_list.html", {"etapas": etapas})


def etapa_procesal_create(request):
    if request.method == "POST":
        form = EtapaProcesalForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Etapa procesal creada correctamente.")
            return redirect("documentos:etapa_procesal_list")
    else:
        form = EtapaProcesalForm()
    return render(request, "documentos/etapa_procesal_form.html", {"form": form})

# PARA NAVEGACION DEL CONTENIDO EN LAS CARPETAS

def carpeta_detalle(request, carpeta_id=None):
    if carpeta_id:
        carpeta = get_object_or_404(Carpeta, pk=carpeta_id)
        subcarpetas = Carpeta.objects.filter(carpetaPadre=carpeta)
        documentos = Documento.objects.filter(carpeta=carpeta)
    else:
        carpeta = None
        subcarpetas = Carpeta.objects.filter(carpetaPadre__isnull=True)
        documentos = Documento.objects.none()

    return render(
        request,
        "documentos/carpeta_detalle.html",
        {"carpeta": carpeta, "subcarpetas": subcarpetas, "documentos": documentos},
    )


#TipoDocumentoViewSet
from rest_framework import viewsets
from .models import TipoDocumento
from .serializers import TipoDocumentoSerializer

class TipoDocumentoViewSet(viewsets.ModelViewSet):
    queryset = TipoDocumento.objects.all()
    serializer_class = TipoDocumentoSerializer

#EtapaProcesalViewSet
from .models import EtapaProcesal
from .serializers import EtapaProcesalSerializer

class EtapaProcesalViewSet(viewsets.ModelViewSet):
    queryset = EtapaProcesal.objects.all()
    serializer_class = EtapaProcesalSerializer

#DocumentoViewSet
from .models import Documento
from .serializers import DocumentoSerializer

class DocumentoViewSet(viewsets.ModelViewSet):
    queryset = Documento.objects.all()
    serializer_class = DocumentoSerializer

#VersionDocumentoViewSet
from .models import VersionDocumento
from .serializers import VersionDocumentoSerializer

class VersionDocumentoViewSet(viewsets.ModelViewSet):
    queryset = VersionDocumento.objects.all()
    serializer_class = VersionDocumentoSerializer
