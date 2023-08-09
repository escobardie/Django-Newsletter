from django.db import models
from ckeditor.fields import RichTextField
# Create your models here.


class Subscribers(models.Model):
    email = models.EmailField(null=True)
    activo = models.BooleanField(default=True, verbose_name='Activo')
    date = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de suscripción')

    class Meta:
        verbose_name='Suscripción'
        verbose_name_plural='Suscripciones'
        ordering = ['-id']

    def __str__(self):
        return self.email


class MailMessage(models.Model):
    title = models.CharField(max_length=100, null=True)
    # message = models.TextField(null=True) # ORIGINAL
    message = RichTextField(null=True, verbose_name='Mensaje')
    creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')

    class Meta:
        verbose_name='Mensaje'
        verbose_name_plural='Mensajes'
        ordering = ['-id']

    def __str__(self):
        return self.title
