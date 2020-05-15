from django.contrib import admin
from .models import Baan, Schietdag, Reservering


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


admin.site.register(Baan)
admin.site.register(Reservering, ReserveringAdmin)
admin.site.register(Schietdag, SchietdagAdmin)
