"""
Nederlands en engels mixen niet.
English and dutch don't mix
"""
from django.shortcuts import render, HttpResponse, Http404
from django.utils import timezone
from .models import Schietdag, Baan, Reservering
import datetime
from django.db.models import Max
from collections import namedtuple
from .forms import ReserveringForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from reserveringssysteem_eemschutters import global_settings
from django.views.decorators.http import require_http_methods
from django.urls import reverse
from django.contrib import messages
import pytz


def get_view_date():
    # return timezone.get_current_timezone().localize(datetime.datetime(year=2020, month=5, day=11, hour=0, minute=20, second=00), is_dst=None)
    return timezone.now()


def daterange(start_date, end_date):
    """
    Generator voor dagen in range. 
    Credits: https://stackoverflow.com/a/1060330
    """
    for n in range(int((end_date - start_date).days)):
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
            schietdagen_in_venster.append((dag, schietdagen[dag.weekday()]))
    return schietdagen_in_venster


@login_required(login_url='/login/')
def mijn_reserveringen(request):
    # Ik heb hier een dag vanaf gehaald, zodat ook de huidige dag getoond wordt.
    view_date = get_view_date() + datetime.timedelta(days=-1)
    reservering = Reservering.objects.filter(start__gte=view_date,
                                             gebruiker=request.user).order_by('start')
    sleutelhouder = request.user.groups.filter(name='Sleutelhouders').exists()

    return render(request, 'reserveringen/mijn_reserveringen.html', {'reserveringen': reservering, 'sleutelhouder': sleutelhouder})


@login_required(login_url='/login/')
@require_http_methods(['POST'])
def verwijder_reserveringen(request):
    view_date = get_view_date()
    target = Reservering.objects.get(
        id=request.POST['reservering_id'], gebruiker=request.user)
    if target.start - datetime.timedelta(hours=1) < view_date:
        messages.error(
            request, 'De reservering kan niet meer worden geannuleerd wanneer deze binnen een uur start.')
    else:
        target.delete()
    return HttpResponseRedirect(reverse('mijn_reserveringen'))


Slot = namedtuple("Slot", ["datum",
                           "starttijd",
                           "eindtijd",
                           "baan",
                           "status",
                           "reservering_eigenaar",
                           'form'])


@login_required(login_url='/login/')
def reserveringen(request, overzicht=False):
    view_date = get_view_date()
    sleutelhouder = request.user.groups.filter(name='Sleutelhouders').exists()
    if overzicht and not(sleutelhouder):
        raise Http404()
    

    if request.method == 'POST':
        # Create a reservation
        form = ReserveringForm(request.POST)
        if form.is_valid():
            # Is de reservering al verlopen?
            args = form.cleaned_data
            if args['eind'] < view_date:
                pass

            else:
                # Heeft deze gebruiker al een reservering deze avond?
                dag_reserveringen = Reservering.objects.filter(start__date=args['start'].date(),
                                                               gebruiker=request.user)
                
                if dag_reserveringen:
                    messages.error(
                            request, f"""Je hebt al een reservering voor deze dag. Je kan een reservering annuleren via <a href="{reverse('mijn_reserveringen')}">Mijn reserveringen</a>.""")
                    pass

                else:
                    # Heeft deze gebruiker al teveel reserveringen deze week?
                    reservering_weekstart = args['start'] - \
                        datetime.timedelta(args['start'].weekday())
                    reservering_weekeind = args['start'] + \
                        datetime.timedelta(6 - args['start'].weekday())
                    week_reserveringen = Reservering.objects.filter(start__date__gte=reservering_weekstart.date(),
                                                                    start__date__lte=reservering_weekeind.date(), gebruiker=request.user)

                    if len(week_reserveringen) >= global_settings.reserveringen_per_week:
                        messages.error(
                            request, f"""Je hebt het maximum({global_settings.reserveringen_per_week}) aantal reserveringen voor deze week. Je kan een reservering annuleren via <a href="{reverse('mijn_reserveringen')}">Mijn reserveringen</a>.""")
                        pass

                    else:
                        # Bestaat deze Reservering al?
                        slot_reserveringen = Reservering.objects.filter(**args)

                        if slot_reserveringen:
                            pass

                        else:
                            # Validation voltooid en geslaag
                            args = {**{'gebruiker': request.user},
                                    **form.cleaned_data}
                            Reservering(**args).save()
        if 'next' in request.GET:
            return HttpResponseRedirect(request.path_info + f"?next={request.GET['next']}")
        else:
            return HttpResponseRedirect(request.path_info)

    dagkeuze = 0
    if request.GET.get('next'):
        try:
            dagkeuze = int(request.GET['next'])
            if dagkeuze < 0:
                dagkeuze = 0
        except ValueError:
            dagkeuze = 0

    schietdagen = Schietdag.objects.order_by('dag')
    schietdagen = alle_schietdagen_in_venster(
        view_date, global_settings.reserveer_venster, schietdagen)

    if dagkeuze > len(schietdagen) - 1:
        dagkeuze = len(schietdagen)

    gekozen_schietdag_datum, gekozen_schietdag = schietdagen[dagkeuze]
    slot_tijden = gekozen_schietdag.slot_tijden()
    banen = Baan.objects.all()

    slots_per_baan = {}

    for baan in banen:

        slots_per_baan[baan] = []

        for slot_tijd in slot_tijden:
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

                if reservering[0].gebruiker == request.user:
                    status = "Zelf"
            else:
                if slot_eind < view_date:
                    status = "Verlopen"
                else:
                    status = "Vrij"

            slot_form = ReserveringForm(initial={
                'start': slot_start,
                'eind': slot_eind,
                'baan': baan.pk,
                'schietdag': gekozen_schietdag.pk})

            slots_per_baan[baan].append(
                Slot(gekozen_schietdag_datum,
                     slot_tijd[0],
                     slot_tijd[1],
                     baan,
                     status,
                     reservering[0].gebruiker.username if reservering else None,
                     slot_form))

    context = {'view_date': view_date,
               'schietdagen': schietdagen,
               'gekozen_schietdag_datum': gekozen_schietdag_datum,
               'banen': banen,
               'slot_tijden': slot_tijden,
               'slots_per_baan': slots_per_baan,
               'dagkeuze': dagkeuze,
               'sleutelhouder':sleutelhouder}

    if not overzicht:
        return render(request, 'reserveringen/reserveringen.html', context)
    else:
        return render(request, 'reserveringen/reserveringen_overzicht.html', context)
