from django.db import models
from actores.models import Actor, Cliente
from seguridad.models import Usuario
from django.conf import settings

# Create your models here.

# ==========================
# CASO
# ==========================
class Caso(models.Model):
    nroCaso = models.CharField(max_length=50, unique=True)
    tipoCaso = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    estado = models.CharField(max_length=20, default="ABIERTO")
    prioridad = models.CharField(max_length=20, default="MEDIA")
    fechaInicio = models.DateField()
    fechaFin = models.DateField(null=True, blank=True)

    # Campos de auditoría
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='casos_creados',
        null=True, blank=True
    )
    modificado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='casos_modificados',
        null=True, blank=True
    )

    creadoEn = models.DateTimeField(auto_now_add=True)
    actualizadoEn = models.DateTimeField(auto_now=True)


# ==========================
# EQUIPO DE CASO (N:M Actor<->Caso)
# PK compuesta lógica: (idActor, idCaso)
# ==========================
class EquipoCaso(models.Model):
    ROL_CHOICES = (
        ("RESPONSABLE", "Responsable"),
        ("ASOCIADO", "Asociado"),
        ("ASISTENTE", "Asistente"),
    )

    actor = models.ForeignKey(Actor, on_delete=models.PROTECT, db_index=True)
    caso = models.ForeignKey(Caso, on_delete=models.CASCADE, db_index=True)
    rolEnEquipo = models.CharField(max_length=20, choices=ROL_CHOICES)
    observaciones = models.TextField(blank=True)
    fechaAsignacion = models.DateField()
    fechaSalida = models.DateField(null=True, blank=True)

    # Campos de auditoría
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='equipocaso_creados',
        null=True, blank=True
    )
    modificado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='equipocaso_modificados',
        null=True, blank=True
    )

    class Meta:
        unique_together = (("actor", "caso"),)
        indexes = [
            models.Index(fields=["caso", "rolEnEquipo"]),
            models.Index(fields=["actor", "caso"]),
        ]

    def __str__(self):
        return f"{self.actor_id} en {self.caso.nroCaso} ({self.rolEnEquipo})"



# ==========================
# PARTE PROCESAL (Cliente<->Caso)
# PK compuesta lógica: (idActor, idCaso) pero idActor refiere a Cliente(idActor)
# ==========================
class ParteProcesal(models.Model):
    ROL_CHOICES = (
        ("DEMANDANTE", "Demandante"),
        ("DEMANDADO", "Demandado"),
        ("TERCERO", "Tercero"),
    )

    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, db_index=True)
    caso = models.ForeignKey(Caso, on_delete=models.CASCADE, db_index=True)
    rolProcesal = models.CharField(max_length=20, choices=ROL_CHOICES)
    estado = models.CharField(max_length=20, default="ACTIVO")
    fechaInicio = models.DateField()
    fechaFin = models.DateField(null=True, blank=True)

    # 🧾 Campos de auditoría
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="parteprocesal_creados",
        null=True, blank=True
    )
    modificado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="parteprocesal_modificados",
        null=True, blank=True
    )

    class Meta:
        unique_together = (("cliente", "caso"),)
        indexes = [
            models.Index(fields=["caso", "rolProcesal"]),
            models.Index(fields=["cliente", "caso"]),
        ]

    def __str__(self):
        return f"{self.cliente} - {self.caso.nroCaso} ({self.rolProcesal})"



# ==========================
# EXPEDIENTE (1–a–1 con Caso)
# ==========================
class Expediente(models.Model):
    caso = models.OneToOneField(Caso, on_delete=models.CASCADE, related_name="expediente")
    nroExpediente = models.CharField(max_length=50)
    estado = models.CharField(max_length=20, default="ABIERTO")
    fechaCreacion = models.DateField()

    # 🧾 Auditoría
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="expediente_creados",
        null=True, blank=True
    )
    modificado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="expediente_modificados",
        null=True, blank=True
    )

    class Meta:
        indexes = [
            models.Index(fields=["estado"]),
            models.Index(fields=["fechaCreacion"]),
        ]

    def __str__(self):
        return f"Expediente {self.nroExpediente} / {self.caso.nroCaso}"



# ==========================
# CARPETA (en el EXPEDIENTE, con jerarquía opcional)
# ==========================
class Carpeta(models.Model):
    expediente = models.ForeignKey(Expediente, on_delete=models.CASCADE, related_name="carpetas")
    nombre = models.CharField(max_length=120)
    estado = models.CharField(max_length=20, default="ACTIVO")
    carpetaPadre = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="subcarpetas"
    )

    # 🧾 Auditoría
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="carpeta_creadas",
        null=True, blank=True
    )
    modificado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="carpeta_modificadas",
        null=True, blank=True
    )

    creadoEn = models.DateTimeField(auto_now_add=True)
    actualizadoEn = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["expediente", "estado"]),
            models.Index(fields=["carpetaPadre"]),
        ]

    def __str__(self):
        return f"{self.nombre} (Expediente {self.expediente_id})"


# GESTION DE TIMELINE PARA LOS EXPEDIENTES

class EventoExpediente(models.Model):
    """
    Registra eventos importantes dentro de un expediente (timeline)
    """
    expediente = models.ForeignKey(
        'Expediente',
        on_delete=models.CASCADE,
        related_name='eventos'
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    tipo = models.CharField(max_length=50)  # 'CARPETA', 'DOCUMENTO', 'VERSION'
    descripcion = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha']
        verbose_name = "Evento de Expediente"
        verbose_name_plural = "Eventos de Expediente"

    def __str__(self):
        return f"[{self.fecha:%d/%m/%Y %H:%M}] {self.tipo}: {self.descripcion}"
