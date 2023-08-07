from django.shortcuts import render, redirect
from . forms import SubscibersForm, MailMessageForm
from . models import Subscribers
from django.contrib import messages
from django.core.mail import send_mail
from django_pandas.io import read_frame

# Create your views here.


def index(request):
    if request.method == 'POST':
        form = SubscibersForm(request.POST)
        print(request.POST['email']) # obtego el correo enviado par
        email_validator= request.POST['email']
        emails = Subscribers.objects.filter(email=email_validator)
        print(emails)
        if emails:
            print("Email ya Suscripto")
            messages.success(request, 'Email ya Suscripto')
            return redirect('/')
        
        else:
            print("Email cargado")
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
    # OBTENEMOS TODOS LOS CORREO QUE ESTEN ACTIVOS
    emails = Subscribers.objects.filter(activo=True)
    # emails = Subscribers.objects.all() # original TRAE TODOS LOS CORREOS
    df = read_frame(emails, fieldnames=['email'])
    mail_list = df['email'].values.tolist()
    print(mail_list)
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
                html_message=message,
            )
            messages.success(request, 'El mensaje ha sido enviado a la lista de correo')
            return redirect('mail-letter')
    else:
        form = MailMessageForm()
    context = {
        'form': form,
    }
    return render(request, 'letter/mail_letter.html', context)
