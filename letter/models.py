from django.db import models
from ckeditor.fields import RichTextField
# Create your models here.


class Subscribers(models.Model):
    email = models.EmailField(null=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


class MailMessage(models.Model):
    title = models.CharField(max_length=100, null=True)
    # message = models.TextField(null=True) # ORIGINAL
    message = RichTextField(null=True, verbose_name='message')

    class Meta:
        verbose_name='Mensaje'
        verbose_name_plural='Mensajes'
        ordering = ['title']

    def __str__(self):
        return self.title
