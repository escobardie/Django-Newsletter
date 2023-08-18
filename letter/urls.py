from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='letter-index'), # SUSCRIPCION BASADA EN FUNCION
    path('mail_letter/', views.mail_letter, name='mail-letter'), # CREACION DE BOLETIN BASADA EN FUNCION
    
    ################# PAGINA LISTADO DE EMAILS EN HTML #################
    path('listing_letter/', views.ListNewslatterView.as_view(), name='lista_boletin'), 
    path('detail_boletin/<int:id>/',views.NewslatterDetailView.as_view(), name='detail_boletin'),
    path('listing_emails/', views.ListEmailsView.as_view(), name='lista_emails'),

    ################# REENVIO DE BOLETIN #################
    path('reenvio_boletin/<int:id>/',views.NewslatterUpdateView.as_view(), name='reenvio_boletin'),
    
    ################# DEF TO CLASS #################
    path('inicio/', views.SubcriptioView.as_view(), name='suscripcion'), # SUSCRIPCION BASADA EN CLASES
    path('create_letter/', views.CreateLetterView.as_view(), name='create_letter'), # CREACION DE BOLETIN BASADA EN CLASES
    ################# DEF TO CLASS #################

    #####################################
    # path('activate/<uidb64>/<token>', views.activate, name='activate'),
    path("activado/", views.ActivateView.as_view(), name="sub_activado"),
    #####################################
    path('activate/<str:uidb64>/<str:token>/', views.ConfirmationView.as_view(), name='activate'),
]
