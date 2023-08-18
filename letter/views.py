from django.shortcuts import render, redirect
from . forms import SubscibersForm, MailMessageForm
from . models import Subscribers, MailMessage
from django.contrib import messages
from django.core.mail import send_mail
from django_pandas.io import read_frame
from django.views.generic import TemplateView, ListView, DetailView, View
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse


from typing import Protocol
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from .tokens_2 import default_token_generator

# Create your views here.

def activateEmail(request, user, to_email):
    mail_subject = "Link de activacion de boletines."
    message = render_to_string("template_activate_account.html", {
        #'user': user.id,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': default_token_generator.make_token(user),
        "protocol": 'https' if request.is_secure() else 'http'
    })
    
    email_list =(to_email,)# LO CONVERTIMOS
    
    ####################################
    if send_mail(
            mail_subject, # (subject)
            '', # message, # ORIGINAL (message)
            'VERIFICACION DE CORREO', # (from_email)
            email_list, # (recipient_list)
            fail_silently=False,
            html_message=message, # AQUI EL MESAJE SE CONVIERTE EN HTML
        ):
        print('ENVIADO')
        messages.success(request, f'Se envio link de verificacion a: "{user}", verifique su casilla de correo.')
    ####################################
    else:
        messages.error(request, f'Problema al enviar correo electrónico a {to_email}, verifica si lo escribiste correctamente.')


class ActivateView(TemplateView):
    template_name = "activado.html"


class ConfirmationView(View):
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = Subscribers.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError,Subscribers.DoesNotExist):
            # Manejar enlace inválido o usuario no encontrado
            messages.error(request, "El enlace de confirmación es inválido.")
            return redirect('sub_activado')  # Redirigir a la página de inicio de sesión o donde desees
        
        if default_token_generator.check_token(user, token):
            user.activo = True
            user.save()

            messages.success(request, "¡Tu cuenta ha sido activada! Ahora puedes recibir boletines.")
        else:
            # Manejar token inválido
            messages.error(request, "El enlace de confirmación es inválido.")
        
        return redirect('sub_activado')  # Redirigir a la página de inicio de sesión o donde desees

####################### DEF TO CLASS #######################
class SubcriptioView(CreateView):
    model = Subscribers
    template_name = 'letter/inicio.html'
    form_class = SubscibersForm
    success_url = reverse_lazy('suscripcion')

    def form_valid(self, form):
        email_validator = self.request.POST['email'] # OBTENEMOS EL EMAIL PURO DEL FORMULARIO
        emails = Subscribers.objects.filter(email=email_validator) # FILTRAMOS SI YA EXISTE EL EMAIL DENTRO DE LA BD

        if emails:
            print("Email ya Suscripto")
            messages.success(self.request, 'Email ya Suscripto') # CREAMOS EL MSJ
            return redirect('suscripcion') # LO REDIRECIONAMOS NUEVAMENTE A LA PAGINA
        else:
            user = form.save()
            user.activo=False
            print('EMAIL: ',form.cleaned_data.get('email'))
            print()
            print('ID: ',user.id)
            print('DOMINIO: ',get_current_site(self.request).domain)
            print('UID-PK: ',urlsafe_base64_encode(force_bytes(user.pk)))
            print('TOKEN: ',default_token_generator.make_token(user))
            activateEmail(self.request, user, form.cleaned_data.get('email'))
            return super().form_valid(form)
    
class CreateLetterView(CreateView):
    model = MailMessage
    template_name = 'letter/create_letter.html'
    form_class = MailMessageForm
    success_url = reverse_lazy('create_letter')

    def form_valid(self, form):
        # OBTENEMOS TODOS LOS CORREO QUE ESTEN ACTIVOS
        emails = Subscribers.objects.filter(activo=True)
        df = read_frame(emails, fieldnames=['email'])
        mail_list = df['email'].values.tolist() # OBTENEMOS LA LISTA DE CORREOS
        form.save() # GUARDAMOS EL FORMULARIO
        title = form.cleaned_data.get('title')
        message = form.cleaned_data.get('message')
        send_mail(
            title, # (subject)
            '', # message, # ORIGINAL (message)
            'PRUEBA DESDE CLASS', # (from_email)
            mail_list, # (recipient_list)
            fail_silently=False,
            html_message=message, # AQUI EL MESAJE SE CONVIERTE EN HTML
        )
        messages.success(self.request, 'El mensaje ha sido enviado a la lista de correo')
        return redirect('create_letter')

####################### DEF TO CLASS #######################


################# PAGINA LISTADO DE EMAILS EN HTML #################
class ListNewslatterView(ListView):
    model: MailMessage
    template_name = 'letter/listing_letter.html'
    context_object_name = 'lista_boletines'
    # paginate_by = 3
    queryset = MailMessage.objects.all() # OBTENEMOS TODOS LOS CORREOS

class NewslatterDetailView(DetailView):
    model = MailMessage
    template_name = 'letter/detail_boletin.html'
    context_object_name = 'boletin'
    pk_url_kwarg = 'id'

class NewslatterUpdateView(UpdateView):
    model = MailMessage
    template_name = 'letter/reenvio_boletin.html'
    form_class = MailMessageForm
    pk_url_kwarg = 'id'

    def get_success_url(self):
        ################# REENVIO DE BOLETIN ################
        emails = Subscribers.objects.filter(activo=True)
        df = read_frame(emails, fieldnames=['email'])
        mail_list = df['email'].values.tolist()
        # print(mail_list)
        titulo = self.object.title
        message = self.object.message
        send_mail(
                titulo, # (subject)
                '', # message, # ORIGINAL (message)
                'PRUEBA DE REENVIO DE BOLETIN', # (from_email)
                mail_list, # (recipient_list)
                fail_silently=False,
                html_message=message, # AQUI EL MESAJE SE CONVIERTE EN HTML
            )
        ################# REENVIO DE BOLETIN ################

        # Obtiene el artículo actualizado desde el contexto
        boletin = self.object
        return reverse('detail_boletin', kwargs={'id': boletin.id})

################# PAGE LISTING EMAILS #################
class ListEmailsView(ListView):
    model: Subscribers
    template_name = 'letter/listing_emails.html' # HTML DONDE SE VERA LA LISTA DE EMALIS
    context_object_name = 'lista_emails' # VARIABLE PARA LA LISTA DE EMAILS
    queryset = Subscribers.objects.filter(activo=True) # OBTENEMOS TODOS LOS EMAILS





############### DEF QUE NO SE USARAN PERO QUEDARA COMO GUIA ###############
def index(request):
    if request.method == 'POST':
        form = SubscibersForm(request.POST)
        print(request.POST['email']) # obtego el correo enviado par
        email_validator= request.POST['email']
        emails = Subscribers.objects.filter(email=email_validator)
        # print(emails)
        
        if emails:
            print("Email ya Suscripto")
            messages.success(request, 'Email ya Suscripto')
            return redirect('/')
        
        else:
            # print("Email cargado")
            if form.is_valid():
                form.save()
                # messages.success(request, 'Suscripción exitosa')
                return redirect('/')
    else:
        form = SubscibersForm()
    context = {
        'form': form,
    }
    return render(request, 'letter/index.html', context)

def mail_letter(request):
    print(request)
    # OBTENEMOS TODOS LOS CORREO QUE ESTEN ACTIVOS
    emails = Subscribers.objects.filter(activo=True)
    # emails = Subscribers.objects.all() # original TRAE TODOS LOS CORREOS
    df = read_frame(emails, fieldnames=['email'])
    #print(df)
    mail_list = df['email'].values.tolist()
    #print(mail_list)
    if request.method == 'POST':
        form = MailMessageForm(request.POST)
        if form.is_valid():
            form.save()
            title = form.cleaned_data.get('title')
            message = form.cleaned_data.get('message')
            send_mail(
                title, # (subject)
                '', # message, # ORIGINAL (message)
                'PRUEBA DESDE WEB', # (from_email)
                mail_list, # (recipient_list)
                fail_silently=False,
                html_message=message, # AQUI EL MESAJE SE CONVIERTE EN HTML
            )
            messages.success(request, 'El mensaje ha sido enviado a la lista de correo')
            return redirect('mail-letter')
    else:
        form = MailMessageForm()
    context = {
        'form': form,
    }
    return render(request, 'letter/mail_letter.html', context)
############### DEF QUE NO SE USARAN PERO QUEDARA COMO GUIA ###############