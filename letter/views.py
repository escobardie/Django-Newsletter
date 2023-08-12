from django.shortcuts import render, redirect
from . forms import SubscibersForm, MailMessageForm
from . models import Subscribers, MailMessage
from django.contrib import messages
from django.core.mail import send_mail
from django_pandas.io import read_frame
from django.views.generic import TemplateView, ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse

# Create your views here.


def index(request):
    if request.method == 'POST':
        form = SubscibersForm(request.POST)
        # print(request.POST['email']) # obtego el correo enviado par
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
    mail_list = df['email'].values.tolist()
    # print(mail_list)
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
    queryset = Subscribers.objects.all() # OBTENEMOS TODOS LOS EMAILS