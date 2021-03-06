"""reserveringssysteem_eemschutters URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, reverse_lazy
import reserveringen.views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', reserveringen.views.reserveringen, name='reserveringen'),
    path('overzicht', reserveringen.views.reserveringen,
         name='overzicht', kwargs={'overzicht': True}),
    path('mijn_reservereringen', reserveringen.views.mijn_reserveringen,
         name='mijn_reserveringen'),
    path('verwijder_reservering', reserveringen.views.verwijder_reserveringen,
         name='verwijder_reserveringen'),
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(template_name='reserveringen/login.html'), name='login'),
    path('wachtwoord_wijzigen/', auth_views.PasswordChangeView.as_view(
        template_name='reserveringen/wachtwoord_wijzigen.html', success_url=reverse_lazy('reserveringen')), name='wachtwoord_wijzigen'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout')
]
