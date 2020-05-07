"""
Nederlands en engels mixen niet.
English and dutch don't mix
"""
from django.shortcuts import render, HttpResponse
from django.utils import timezone
from .models import Schietdag, Baan
import datetime
from django.db.models import Max


def next_datetime_with_weekday(current, target):
    """
    credits: https://stackoverflow.com/questions/8801084/how-to-calculate-next-friday/8801540
    """
    target = current + \
        datetime.timedelta(((target-current.weekday()) % 7))
    return target


def index(request):
    # Determine our date based on an optional GET parameter 'next' that offsets to the next available day
    view_date = timezone.now()
    offset = 0
    if request.GET.get('next'):
        try:
            offset = int(request.GET['next'])
            if offset < 0:
                offset = 0
        except ValueError:
            pass


    schietdagen = Schietdag.objects.order_by('dag')
    schietdagen = list(map(lambda schietdag: (next_datetime_with_weekday(
        view_date, schietdag.dag), schietdag), schietdagen))
    schietdagen.sort(key=lambda t: (t[0] - view_date).total_seconds())
    
    if offset > len(schietdagen) - 1:
        offset = len(schietdagen)
    gekozen_schietdag_datum, gekozen_schietdag = schietdagen[offset]
    banen = Baan.objects.all()

    return render(request, 'reserveringen/reserveringen.html', {'view_date': view_date,
                                                                'gekozen_schietdag_datum': gekozen_schietdag_datum,
                                                                'banen': banen,
                                                                'next_offset': offset + 1,
                                                                'prev_offset': offset - 1,
                                                                'laatste': offset == len(schietdagen) - 1,
                                                                'eerste': offset == 0})
