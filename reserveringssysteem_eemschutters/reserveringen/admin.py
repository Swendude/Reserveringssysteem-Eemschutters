from django.contrib import admin
from .models import Baan, Protocol


class ProtocolAdmin(admin.ModelAdmin):
    fields = ['slot_duur',
              'opstart_duur',
              'afbouw_duur',
              'open',
              'sluit',
              'prioriteit',
              'aantal_slots']
    list_display = ['__str__',
                    'slot_duur',
                    'opstart_duur',
                    'afbouw_duur',
                    'open',
                    'sluit',
                    'aantal_slots']
    readonly_fields = ['aantal_slots']


admin.site.register(Baan)
admin.site.register(Protocol, ProtocolAdmin)
