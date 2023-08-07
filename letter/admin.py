from django.contrib import admin
from . models import MailMessage, Subscribers



admin.site.site_header = 'Administración De Suscripciones'
admin.site.index_title = 'Panel de Control'
admin.site.site_title = 'Mensajes'
# Register your models here.


######################
#### Suscriptores ####
######################

class SubscribersAdmin(admin.ModelAdmin):
    readonly_fields = ('email', 'date')
    list_display = ('email', 'activo', 'date')

admin.site.register(Subscribers, SubscribersAdmin)


#####################
#### MailMessage ####
#####################

class MailMessageAdmin(admin.ModelAdmin):
    readonly_fields = ('creacion',)
    list_display = ('title', 'message', 'creacion')

admin.site.register(MailMessage, MailMessageAdmin)

