from django.shortcuts import render, redirect
from . forms import SubscibersForm, MailMessageForm
from . models import Subscribers, MailMessage
from django.contrib import messages
from django.core.mail import send_mail
from django_pandas.io import read_frame
from django.views.generic import TemplateView, ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse


from typing import Protocol
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage
from .tokens import account_activation_token

# Create your views here.
#####################################
def activate(request, uidb64, token):
    # POR LAGUNA RAZON ENTRA DOS VECES CUANDO ACCEDEMOS DESDE EL LINK DEL CORREO
    # ESTA PRIMERA VEZ ENTRA SIN POROBLEMA, MOSTRARIA EL MENSAJE DEL IF PERO..
    # EN LA SEGUNDA BORRA O PISA EL MSJ DEL PRIMER HTML.
    # NO SE DE DONDE VIENE EL ERROR
    
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = Subscribers.objects.get(pk=uid)
    except:
        user = None
        print('ENTRO DESDE EXCEPTION')

    if user is not None and account_activation_token.check_token(user, token):
        print("USUARIO:",user)
        print('ENTRO POR ACA DESDE DEF ACTIVATE')
        user.activo = True
        print(user.activo)
        user.save() # ORIGINAL LUGAR

        messages.success(request, "que ?Gracias por su confirmación por correo electrónico. Ahora puede iniciar sesión en su cuenta.")
        # user.save()
        print("LLEGO HASTA AQUI")
        # return redirect('sub_activado')
    # else:
    #     print("soy el otro USUARIO:",user)
    #     print('Y AHORA ENTRO POR ACA DESDE DEF ACTIVATE')
    #     messages.error(request, "¡El enlace de activación no es válido!")
    #     return redirect('sub_activado')
    
    print('Y POR ACA NO?')
    messages.success(request, "Gracias por su confirmación por correo electrónico. Ahora podra recibir los boletines.")
    return redirect('sub_activado')

def activateEmail(request, user, to_email):
    mail_subject = "Activa tu cuenta de usuario."
    message = render_to_string("template_activate_account.html", {
        'user': user.id,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        "protocol": 'https' if request.is_secure() else 'http'
    })
    email = EmailMessage(mail_subject, message, to=[to_email])
    if email.send():
        messages.success(request, f'Estimado {user}, vaya a la bandeja de entrada de su correo electrónico {to_email} y haga clic en \
                recibido el enlace de activación para confirmar y completar el registro. Nota: Revisa tu carpeta de correo no deseado.')
    else:
        messages.error(request, f'Problema al enviar correo electrónico a {to_email}, verifica si lo escribiste correctamente.')

class ActivateView(TemplateView):
    template_name = "activado.html"


#####################################
####################### DEF TO CLASS #######################
class SubcriptioView(CreateView):
    model = Subscribers
    template_name = 'letter/inicio.html'
    form_class = SubscibersForm
    success_url = reverse_lazy('suscripcion')

    def form_valid(self, form):
        email_validator = self.request.POST['email'] # OBTENEMOS EL EMAIL PURO DEL FORMULARIO
        #print(email_validator)
        emails = Subscribers.objects.filter(email=email_validator) # FILTRAMOS SI YA EXISTE EL EMAIL DENTRO DE LA BD
        #print(emails)

        if emails:
            print("Email ya Suscripto")
            messages.success(self.request, 'Email ya Suscripto') # CREAMOS EL MSJ
            return redirect('suscripcion') # LO REDIRECIONAMOS NUEVAMENTE A LA PAGINA
        else:
            messages.success(self.request, 'Suscripción exitosa')
            #####################################
            user = form.save()
            user.activo=False
            print(form.cleaned_data.get('email'))
            print()
            print(user.id)
            print(get_current_site(self.request).domain)
            print(urlsafe_base64_encode(force_bytes(user.pk)))
            print(account_activation_token.make_token(user))
            activateEmail(self.request, user, form.cleaned_data.get('email'))
            #####################################
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
                messages.success(request, 'Suscripción exitosa')
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

    # def form_valid(self, form):
    #     if form.instance.autor == self.request.user or self.request.user.is_superuser:
    #         return super().form_valid(form)
    #     else:
    #         return redirect('login')

    def get_success_url(self):
        ################# REENVIO DE BOLETIN ################
        # print(self.object.message)
        # OBTENEMOS TODOS LOS CORREO QUE ESTEN ACTIVOS
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
        # mail_letter(boletin)
        # messages.success(request, 'El mensaje ha sido enviado a la lista de correo') # completar luego, aqui debe de generar un msj al eterminar de enviar.
        # Genera la URL para la vista 'articulo' usando el slug actualizado del artículo
        return reverse('detail_boletin', kwargs={'id': boletin.id})

################# PAGE LISTING EMAILS #################
class ListEmailsView(ListView):
    model: Subscribers
    template_name = 'letter/listing_emails.html' # HTML DONDE SE VERA LA LISTA DE EMALIS
    context_object_name = 'lista_emails' # VARIABLE PARA LA LISTA DE EMAILS
    # paginate_by = 3
    queryset = Subscribers.objects.filter(activo=True) # OBTENEMOS TODOS LOS EMAILS