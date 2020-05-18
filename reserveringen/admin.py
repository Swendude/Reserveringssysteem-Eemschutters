from django.contrib import admin
from solo.admin import SingletonModelAdmin
from .models import Baan, Schietdag, Reservering, SiteConfiguration
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User  
from django import forms
from django.urls import path
from django.shortcuts import render, redirect
from collections import Set
import csv
from io import StringIO

class SchietdagAdmin(admin.ModelAdmin):
    fields = ['dag',
              'slot_duur',
              'opstart_duur',
              'afbouw_duur',
              'open',
              'sluit',
              'extra_tijd_begin',
              'extra_tijd_eind',
              'aantal_slots']
    list_display = ['__str__',
                    'slot_duur',
                    'open',
                    'sluit',
                    'aantal_slots']
    readonly_fields = ['aantal_slots']

    def render_change_form(self, request, context, *args, **kwargs):
        # here we define a custom template
        self.change_form_template = 'reserveringen/wijziging_waarschuwing.html'
        extra = {
            'help_text': """PAS OP: Het wijzigen van een schietdag instelling zal alle (ook toekomstige) reserverinen op deze schietdag 
            verwijderen. Stel je gebruikers (tijdig) op de hoogte van een wijziging in schietdag instellingen."""
        }

        context.update(extra)
        return super(SchietdagAdmin, self).render_change_form(request,
                                                           context, *args, **kwargs)


class ReserveringAdmin(admin.ModelAdmin):
    list_display = ['gebruiker', 'start', 'eind', 'baan']
    list_filter = ['gebruiker', 'start']

class CsvImportForm(forms.Form):
    csv_file = forms.FileField()

class CustomUserAdmin(UserAdmin):
     change_list_template = "reserveringen/user_changelist.html"

     def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('import-csv/', self.import_csv),
        ]
        return my_urls + urls

     def import_csv(self, request):
        if request.method == "POST":
            csv_file = request.FILES["csv_file"]
            csv_file = StringIO(csv_file.read().decode())
            reader = csv.DictReader(csv_file, delimiter='|')
            for row in reader:
                User.objects.create_user(**row).save()
            self.message_user(request, "Your csv file has been imported")
            return redirect("..")
        form = CsvImportForm()
        payload = {"form": form}
        return render(
            request, "reserveringen/csv_form.html", payload
        )

admin.site.register(Baan)
admin.site.register(Reservering, ReserveringAdmin)
admin.site.register(Schietdag, SchietdagAdmin)
admin.site.register(SiteConfiguration, SingletonModelAdmin)
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)