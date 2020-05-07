from django.contrib import admin
from .models import Baan, Protocol, Reservering


class ProtocolAdmin(admin.ModelAdmin):
    fields = ['slot_duur',
              'opstart_duur',
              'afbouw_duur',
              'open',
              'sluit',
              'geldig_op',
              'prioriteit',
              'aantal_slots']
    list_display = ['__str__',
                    'slot_duur',
                    'get_geldig_op',
                    'open',
                    'sluit',
                    'aantal_slots']
    readonly_fields = ['aantal_slots']

    def get_geldig_op(self, obj):
        print(obj.dagen)
        return list(map(lambda num: obj.dagen[int(num)], list(obj.geldig_op)))
    get_geldig_op.short_description = 'Geldig op'

class ReserveringAdmin(admin.ModelAdmin):
     def has_add_permission(self, request):
        return False

admin.site.register(Baan)
admin.site.register(Reservering, ReserveringAdmin)
admin.site.register(Protocol, ProtocolAdmin)
