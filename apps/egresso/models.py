from django.db import models

class Egresso(models.Model):
    fullName = models.CharField("Nome Completo", max_length=100, blank=False)
    birthDate = models.DateField("Data de Nascimento", blank=False)
    gender = models.CharField("Gênero", max_length=30, blank=False)
    # curso = models.CharField("Curso", ) FOREIGNKEY
    status = models.CharField("Status", max_length=50, blank=False)
    email = models.CharField("Email", max_length=250, blank=False)
    number = models.CharField("Número", max_length=11, blank=False)

class Meta:
    verbose_name = "Egresso"
    verbose_name_plural = "Egressos"