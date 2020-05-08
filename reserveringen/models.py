from django.db import models
from django.contrib.auth.models import User
import datetime
from django.core.exceptions import ValidationError
from django.utils import timezone

class Baan(models.Model):
    naam = models.CharField(max_length=50)
    mobiel = models.BooleanField()
    afstand = models.IntegerField(help_text='in meters')

    def __str__(self):
        if not self.mobiel:
            return f"Baan {self.naam} ({self.afstand} m)"
        else:
            return f"Baan {self.naam}  (mobiel)"

    class Meta:
        verbose_name_plural = "Banen"


DAGEN = ((0, 'Maandag'),
         (1, 'Dinsdag'),
         (2, 'Woensdag'),
         (3, 'Donderdag'),
         (4, 'Vrijdag'),
         (5, 'Zaterdag'),
         (6, 'Zondag'))


class Schietdag(models.Model):
    """
    Een schietdag is een dag waarop men kan schieten.
    """
    dag = models.IntegerField(choices=DAGEN, unique=True, null=False)
    slot_duur = models.DurationField(help_text='[HH:MM:SS]')
    opstart_duur = models.DurationField(help_text='[HH:MM:SS]')
    afbouw_duur = models.DurationField(help_text='[HH:MM:SS]')
    open = models.TimeField(help_text='[HH:MM:SS]')
    sluit = models.TimeField(help_text='[HH:MM:SS]')


    def __str__(self):
        return dict(DAGEN)[self.dag]

    @property
    def aantal_slots(self):
        """
        Bereken het aantal slots als gevolg van deze instellingen.
        """
        tijd_open = datetime.timedelta(hours=self.sluit.hour - self.open.hour,
                                       minutes=self.sluit.minute - self.open.minute)

        return tijd_open/self.slot_duur
    
    @property
    def dagen(self):
        return dict(DAGEN)

    def slot_tijden(self):
        times = []
        last_time = self.open
        while last_time < self.sluit:
            end_time = (datetime.datetime.combine(timezone.now(), last_time) + self.slot_duur).time()
            times.append((last_time, end_time))
            last_time = end_time
        assert(len(times) == self.aantal_slots)
        return times

    def clean(self):
        """
        Valideer dat het aantal slots een rond getal is.
        """
        if not self.aantal_slots.is_integer():
            raise ValidationError(
                f'Er zijn {self.aantal_slots} slots in dit protocol. Dit moet een rond getal zijn.')

    class Meta:
        verbose_name_plural = 'Schietdagen'
        


class Reservering(models.Model):
    """
    Een reservering is een tijdsduur op een baan.
    """
    start = models.DateTimeField()
    eind = models.DateTimeField()
    baan = models.ForeignKey(Baan, on_delete=models.PROTECT)
    schietdag = models.ForeignKey(Schietdag, on_delete=models.PROTECT)
    gebruiker = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Reservering van {self.gebruiker.username} op {self.start}"

    class Meta:
        verbose_name_plural = "Reserveringen"
