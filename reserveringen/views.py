"""
Nederlands en engels mixen niet.
English and dutch don't mix
"""
from django.shortcuts import render, HttpResponse, Http404
from django.utils import timezone
from .models import Schietdag, Baan, Reservering, SiteConfiguration, NieuwsBericht
import datetime
from django.db.models import Max
from collections import namedtuple, defaultdict
from .forms import ReserveringForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.views.decorators.http import require_http_methods
from django.urls import reverse
from django.contrib import messages
import pytz

global_settings = SiteConfiguration.objects.get


def get_view_date():
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
    current = datetime.datetime.combine(current, datetime.time(12, 0, 0))
    schietdagen = {schietdag.dag: schietdag for schietdag in schietdagen}
    schietdagen_in_venster = []
    for dag in daterange(current, current + venster):
        if dag.weekday() in schietdagen:
            schietdagen_in_venster.append((dag, schietdagen[dag.weekday()]))
    return schietdagen_in_venster


def week_start_eind(datum):
    weekstart = datum - \
        datetime.timedelta(datum.weekday())
    weekeind = datum + \
        datetime.timedelta(6 - datum.weekday())
    weekstart = datetime.datetime.combine(weekstart, datetime.time())
    weekeind = datetime.datetime.combine(weekstart, datetime.time())
    return(weekstart, weekeind)


@login_required(login_url='/login/')
def mijn_reserveringen(request):
    view_date = get_view_date()
    reservering_weekstart, reservering_weekeind = week_start_eind(view_date)
    reserveringen = Reservering.objects.filter(
        start__date__gte=reservering_weekstart.date(), gebruiker=request.user)
    reserveringen_per_week = defaultdict(list)
    for reservering in reserveringen:
        reservering_weekstart, reservering_weekeind = week_start_eind(
            reservering.start)
        if reservering.start < view_date:
            reservering.verlopen = True
        reserveringen_per_week[reservering_weekstart].append(reservering)
    sleutelhouder = request.user.groups.filter(name='Sleutelhouders').exists()
    return render(request, 'reserveringen/mijn_reserveringen.html', {'sleutelhouder': sleutelhouder, 'reserveringen_per_week': dict(reserveringen_per_week)})


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
                           'form',
                           'vogelvrij_slot_form'])


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
            args = form.cleaned_data
            if args['eind'] < view_date:
                # Is de reservering al verlopen?
                pass

            if args['start'] - view_date < datetime.timedelta(hours=1):
                # Dit is een bonusslot, die mag alleen als de gebruiker geen andere reservingen op dit slot heeft
                slot_reserveringen = Reservering.objects.filter(start=args['start'],
                                                                gebruiker=request.user)
                if slot_reserveringen:
                    messages.error(
                        request, f"""Je hebt al een reservering voor dit slot. Je kan een reservering annuleren via <a href="{reverse('mijn_reserveringen')}">Mijn reserveringen</a>.""")
                    pass
                else:
                    args = {**{'gebruiker': request.user},
                            **form.cleaned_data}
                    Reservering(**args).save()

            else:
                # Heeft deze gebruiker al een reservering deze avond?
                dag_reserveringen = Reservering.objects.filter(start__date=args['start'].date(),
                                                               gebruiker=request.user, bonus=False)

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
                                                                    start__date__lte=reservering_weekeind.date(),
                                                                    gebruiker=request.user,
                                                                    bonus=False)

                    if len(week_reserveringen) >= global_settings().reserveringen_per_week:
                        messages.error(
                            request, f"""Je hebt het maximum({global_settings().reserveringen_per_week}) aantal reserveringen voor deze week. Je kan een reservering annuleren via <a href="{reverse('mijn_reserveringen')}">Mijn reserveringen</a>.""")
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
        # else:
        #     print(form.errors)
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
        view_date, global_settings().reserveer_venster, schietdagen)
    if not schietdagen:
        return Http404
    if dagkeuze > len(schietdagen) - 1:
        dagkeuze = len(schietdagen)

    gekozen_schietdag_datum, gekozen_schietdag = schietdagen[dagkeuze]
    slot_tijden = gekozen_schietdag.slot_tijden()
    banen = Baan.objects.all()

    slots_per_baan = {}
    banen_per_slot = {}
    for baan in banen:

        slots_per_baan[baan] = []

        for i, slot_tijd in enumerate(slot_tijden):

            slot_start = timezone.make_aware(
                datetime.datetime.combine(gekozen_schietdag_datum, slot_tijd[0]))
            slot_eind = timezone.make_aware(datetime.datetime.combine(
                gekozen_schietdag_datum, slot_tijd[1]))
            reservering = Reservering.objects.filter(baan=baan,
                                                     schietdag=gekozen_schietdag,
                                                     start=slot_start,
                                                     eind=slot_eind)
            if not slot_tijd[0] in banen_per_slot:
                banen_per_slot[slot_tijd[0]] = []

            if reservering:
                status = "Bezet"

                if reservering[0].gebruiker == request.user:
                    status = "Zelf"
            else:
                if slot_eind < view_date:
                    status = "Verlopen"
                elif slot_start - global_settings().reserveer_stop < view_date:
                    status = "Te laat"
                else:
                    status = "Vrij"
                    if (slot_start - view_date) < datetime.timedelta(hours=1):
                        status = "Vogelvrij"
                    if (baan == global_settings().sleutelhouder_baan and i == global_settings().sleutelhouder_slot):
                        status = "Sleutelhouder"

            slot_form = ReserveringForm(initial={
                'start': slot_start,
                'eind': slot_eind,
                'baan': baan.pk,
                'schietdag': gekozen_schietdag.pk,
                'bonus': False})

            vogelvrij_slot_form = ReserveringForm(initial={
                'start': slot_start,
                'eind': slot_eind,
                'baan': baan.pk,
                'schietdag': gekozen_schietdag.pk,
                'bonus': True})

            slot = Slot(gekozen_schietdag_datum,
                        slot_tijd[0],
                        slot_tijd[1],
                        baan,
                        status,
                        reservering[0].gebruiker if reservering else None,
                        slot_form,
                        vogelvrij_slot_form)

            slots_per_baan[baan].append(slot)
            banen_per_slot[slot_tijd[0]].append(slot)

    context = {'view_date': view_date,
               'schietdagen': schietdagen,
               'gekozen_schietdag_datum': gekozen_schietdag_datum,
               'banen': banen,
               'slot_tijden': slot_tijden,
               'slots_per_baan': slots_per_baan,
               'banen_per_slot': banen_per_slot,
               'dagkeuze': dagkeuze,
               'sleutelhouder': sleutelhouder,
               'nieuwsbericht': NieuwsBericht.objects.all().order_by('gewijzigd_op').all()[0] or None}

    if not overzicht:
        return render(request, 'reserveringen/reserveringen.html', context)
    else:
        return render(request, 'reserveringen/reserveringen_overzicht.html', context)
