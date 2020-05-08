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

Slot = namedtuple("Slot", ["datum", "starttijd", "eindtijd", "baan", "status", 'form'])


def next_datetime_with_weekday(current, target):
    """
    credits: https://stackoverflow.com/questions/8801084/how-to-calculate-next-friday/8801540
    """
    target = current + \
        datetime.timedelta(((target-current.weekday()) % 7))
    return target

@login_required(login_url='/admin/')
def index(request):
    if request.method == 'POST':
        # Create a reservation
        form = ReserveringForm(request.POST)
        if form.is_valid():
            args = {**{'gebruiker': request.user}, **form.cleaned_data}
            Reservering(**args).save()
            
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
    schietdagen = list(map(lambda schietdag: (next_datetime_with_weekday(
        view_date, schietdag.dag), schietdag), schietdagen))
    schietdagen.sort(key=lambda t: (t[0] - view_date).total_seconds())

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
            if reservering:
                status = "Bezet"
            slot_form = ReserveringForm(initial={
                'start':slot_start,
                'eind':slot_eind,
                'baan':baan.pk,
                'schietdag':gekozen_schietdag.pk})
            slots_per_baan[baan].append(
                Slot(gekozen_schietdag_datum, slot_tijd[0], slot_tijd[1], baan, status, slot_form))

    return render(request, 'reserveringen/reserveringen.html', {'view_date': view_date,
                                                                'schietdagen': schietdagen,
                                                                'gekozen_schietdag_datum': gekozen_schietdag_datum,
                                                                'banen': banen,
                                                                'slot_tijden': slot_tijden,
                                                                'slots_per_baan': slots_per_baan,
                                                                'choice': dagkeuze})
