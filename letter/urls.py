from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='letter-index'),
    path('mail_letter/', views.mail_letter, name='mail-letter'),
    
    ################# PAGINA LISTADO DE EMAILS EN HTML #################
    path('listing_letter/', views.ListNewslatterView.as_view(), name='lista_boletin'),
    path('detail_boletin/<int:id>/',views.NewslatterDetailView.as_view(), name='detail_boletin'),
    # path('reenvio_boletin/<int:id>/',views.NewslatterUpdateView.as_view(), name='reenvio_boletin'),
    path('reenvio_boletin/<int:id>/',views.NewslatterUpdateView.as_view(), name='reenvio_boletin'),

    path('listing_emails/', views.ListEmailsView.as_view(), name='lista_emails'),
]
