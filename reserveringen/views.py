"""
Nederlands en engels mixen niet.
English and dutch don't mix
"""
from django.shortcuts import render, HttpResponse
from django.utils import timezone
from .models import Schietdag, Baan, Reservering
import datetime
from django.db.models import Max
from collections import namedtuple
from .forms import ReserveringForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from reserveringssysteem_eemschutters import global_settings

Slot = namedtuple("Slot", ["datum", "starttijd", "eindtijd", "baan", "status", 'form', 'zelf'])


def daterange(start_date, end_date):
    """
    Generator voor dagen in range. 
    Credits: https://stackoverflow.com/a/1060330
    """
    for n in range(int ((end_date - start_date).days)):
        yield start_date + datetime.timedelta(n)



def alle_schietdagen_in_venster(current, venster, schietdagen):
    """
    Verkrijg alle dagen die schietdagen zijn binnen het huidige venster (timedelta). 
    Geeft een lijst van tuples (datum, schietdag) terug.
    """
    schietdagen = {schietdag.dag: schietdag for schietdag in schietdagen}
    schietdagen_in_venster = []
    for dag in daterange(current, current + venster):
        if dag.weekday() in schietdagen:
            schietdagen_in_venster.append((dag,schietdagen[dag.weekday()]))
    return schietdagen_in_venster


@login_required(login_url='/login/')
def mijn_reserveringen(request):
    # Ik heb hier een dag vanaf gehaald, zodat ook de huidige dag getoond wordt.
    view_date = timezone.now() + datetime.timedelta(days=-1)
    reservering = Reservering.objects.filter(start__gte=view_date,
                                                gebruiker=request.user).order_by('start')
    return render(request, 'reserveringen/mijn_reserveringen.html', {'reserveringen':reservering})


@login_required(login_url='/login/')
def reserveringen(request, overzicht=False):
    if request.method == 'POST':
        # Create a reservation
        form = ReserveringForm(request.POST)
        if form.is_valid():
            args = {**{'gebruiker': request.user}, **form.cleaned_data}
            # TODO: Bestaat Reservering al?!
            Reservering(**args).save()
        if 'next' in request.GET:
            return HttpResponseRedirect(request.path_info + f"?next={request.GET['next']}")
        else:
            return HttpResponseRedirect(request.path_info)
            
    # Determine our date based on an optional GET parameter 'next' that offsets to the next available day
    view_date = timezone.now()
    # Set our time to UTC 12:00:00, this should work with the math we do in `next_datetime_with_weekdays`
    # without being bothered with timezone. I think we can handle timezones up to UTC +/- 12(ish).
    view_date = view_date + datetime.timedelta(days=0,
                                               hours=12 - view_date.time().hour,
                                               minutes=-view_date.time().minute,
                                               seconds=-view_date.time().second)

    dagkeuze = 0
    if request.GET.get('next'):
        try:
            dagkeuze = int(request.GET['next'])
            if dagkeuze < 0:
                dagkeuze = 0
        except ValueError:
            dagkeuze = 0

    schietdagen = Schietdag.objects.order_by('dag')
    schietdagen = alle_schietdagen_in_venster(view_date, global_settings.reserveer_venster, schietdagen)

    if dagkeuze > len(schietdagen) - 1:
        dagkeuze = len(schietdagen)

    gekozen_schietdag_datum, gekozen_schietdag = schietdagen[dagkeuze]
    slot_tijden = gekozen_schietdag.slot_tijden()
    banen = Baan.objects.all()

    slots_per_baan = {}
    for baan in banen:
        slots_per_baan[baan] = []
        for slot_tijd in slot_tijden:
            status = "Vrij"
            slot_start = timezone.make_aware(
                datetime.datetime.combine(gekozen_schietdag_datum, slot_tijd[0]))
            slot_eind = timezone.make_aware(datetime.datetime.combine(
                gekozen_schietdag_datum, slot_tijd[1]))
            reservering = Reservering.objects.filter(baan=baan,
                                                     schietdag=gekozen_schietdag,
                                                     start=slot_start,
                                                     eind=slot_eind)
            zelf = False
            if reservering:
                status = "Bezet"
                if reservering[0].gebruiker == request.user:
                    zelf=True
            slot_form = ReserveringForm(initial={
                'start':slot_start,
                'eind':slot_eind,
                'baan':baan.pk,
                'schietdag':gekozen_schietdag.pk})
            slots_per_baan[baan].append(
                Slot(gekozen_schietdag_datum, slot_tijd[0], slot_tijd[1], baan, status, slot_form, zelf))
    
    if not overzicht:
        return render(request, 'reserveringen/reserveringen.html', {'view_date': view_date,
                                                                    'schietdagen': schietdagen,
                                                                    'gekozen_schietdag_datum': gekozen_schietdag_datum,
                                                                    'banen': banen,
                                                                    'slot_tijden': slot_tijden,
                                                                    'slots_per_baan': slots_per_baan,
                                                                    'choice': dagkeuze})
    else:
        return render(request, 'reserveringen/reserveringen_overzicht.html', {'view_date': view_date,
                                                                    'schietdagen': schietdagen,
                                                                    'gekozen_schietdag_datum': gekozen_schietdag_datum,
                                                                    'banen': banen,
                                                                    'slot_tijden': slot_tijden,
                                                                    'slots_per_baan': slots_per_baan,
                                                                    'choice': dagkeuze})