from django.urls import path, re_path

from pagina_web.views import Cambiar_Contra, Cambiar_Usuario, CerrarSesion, Clientes, Home, Registros, Reporte_registro,Usuario, Inicio, Login, Redirigir, Registro, Resumen
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView

urlpatterns=[
    path('', Redirigir.as_view(), name='index'),
    path('login', Login.as_view(), name='login'),
    path('inicio', Inicio.as_view(), name='inicio'),
    path('registro', Registro.as_view(), name='registro'),
    path('cambiar_usuario', Cambiar_Usuario.as_view(), name='cambiar_usuario'),
    path('cambiar_contra', Cambiar_Contra.as_view(), name='cambiar_contra'),
    path('home', Home.as_view(), name='home'),
    path('usuario', Usuario.as_view(), name='usuario'),
    path('resumen', Resumen.as_view(), name='resumen'),
    path('logout', CerrarSesion.as_view(), name='logout'),
    path('clientes', Clientes.as_view(), name='clientes'),
    path('registros', Registros.as_view(), name='registros'),
    path('reporte_registro', Reporte_registro.as_view(), name='reporte_registro'),
    
    #Recuperar Contra
    path('reset/password_reset', PasswordResetView.as_view(template_name='recuperar_contra/recuperar_contra.html', email_template_name="recuperar_contra/plantilla_email.html"), name = 'password_reset'),
    path('reset/password_reset_done', PasswordResetDoneView.as_view(template_name='recuperar_contra/recuperar_contra_done.html'), name = 'password_reset_done'),
    re_path(r'^reset/(?P<uidb64>[0-9A-za-z_\-]+)/(?P<token>.+)/$', PasswordResetConfirmView.as_view(template_name='recuperar_contra/recuperar_contra_confirm.html'), name = 'password_reset_confirm'),
    path('reset/done',PasswordResetCompleteView.as_view(template_name='recuperar_contra/recuperar_contra_complete.html') , name = 'password_reset_complete'),
]