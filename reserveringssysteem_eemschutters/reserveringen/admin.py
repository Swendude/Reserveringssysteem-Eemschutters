from django.contrib import admin
from .models import Baan, Schietdag, Reservering


class SchietdagAdmin(admin.ModelAdmin):
    fields = ['dag',
    'slot_duur',
              'opstart_duur',
              'afbouw_duur',
              'open',
              'sluit',
              'aantal_slots']
    list_display = ['__str__',
                    'slot_duur',
                    'open',
                    'sluit',
                    'aantal_slots']
    readonly_fields = ['aantal_slots']


class ReserveringAdmin(admin.ModelAdmin):
     def has_add_permission(self, request):
        return False

admin.site.register(Baan)
admin.site.register(Reservering, ReserveringAdmin)
admin.site.register(Schietdag, SchietdagAdmin)
