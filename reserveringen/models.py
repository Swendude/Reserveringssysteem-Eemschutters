from django.db import models
from django.contrib.auth.models import User
import datetime
from django.core.exceptions import ValidationError
from django.utils import timezone
from solo.models import SingletonModel


def time_add_timedelta(t, td):
    """
    Combineer een time object met een timedelta object.
    Bidden naar de timezone goden.
    """
    return (datetime.datetime.combine(timezone.now(), t) + td).time()


class Baan(models.Model):
    naam = models.CharField(max_length=50)
    label = models.CharField(max_length=140)

    def __str__(self):
        if self.label != "":
            return f"Baan {self.naam} ({self.label})"
        else:
            return f"Baan {self.naam}"

    class Meta:
        verbose_name_plural = "Banen"
        ordering = ['naam']


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
    slot_duur = models.DurationField(
        help_text='[HH:MM:SS] Overgebleven tijd zal worden toegevoegd aan het eerste en laatste slot.')
    opstart_duur = models.DurationField(
        help_text='[HH:MM:SS] Hoelang van te voren mogen deelnemers aanwezig zijn?')
    afbouw_duur = models.DurationField(
        help_text='[HH:MM:SS] Hoelang mogen deelnemers na het slot einde aanwezig zijn?')
    extra_tijd_begin = models.DurationField(
        help_text='[HH:MM:SS] Als er tijd onverdeeld blijft door je slotkeuze, verdeel deze als extra aan het begin en eind')
    extra_tijd_eind = models.DurationField(
        help_text='[HH:MM:SS] Als er tijd onverdeeld blijft door je slotkeuze, verdeel deze als extra aan het begin en eind')
    open = models.TimeField(help_text='[HH:MM:SS]')
    sluit = models.TimeField(help_text='[HH:MM:SS]')

    def __str__(self):
        return dict(DAGEN)[self.dag]

    def save(self, *args, **kwargs):
        mijn_reserveringen = Reservering.objects.filter(schietdag=self)
        mijn_reserveringen.delete()
        super().save(*args, **kwargs)

    @property
    def tijd_open(self):
        """
        Een timedelta voor de totale duur van de opening
        """
        return datetime.timedelta(hours=self.sluit.hour - self.open.hour,
                                  minutes=self.sluit.minute - self.open.minute)

    @property
    def aantal_slots(self):
        """
        Bereken het aantal slots als gevolg van deze instellingen.
        """
        return int(self.tijd_open/self.slot_duur)

    @property
    def dagen(self):
        return dict(DAGEN)

    def sf_dag(self):
        return self.dagen[self.dag]

    def slot_tijden(self):
        tijden = []

        # Houd rekening met de extra begintijd
        tijden.append((self.open, time_add_timedelta(
            self.open, self.slot_duur + self.extra_tijd_begin)))
        begin_tijd = tijden[0][1]

        while time_add_timedelta(begin_tijd, self.slot_duur) <= self.sluit:
            eind_tijd = time_add_timedelta(begin_tijd, self.slot_duur)
            tijden.append((begin_tijd, eind_tijd))
            begin_tijd = eind_tijd

        # Houd rekening met de extra eindtijd
        tijden[-1] = (tijden[-1][0],
                      time_add_timedelta(tijden[-1][1], self.extra_tijd_eind))
        if not len(tijden) == self.aantal_slots:
             raise ValidationError(
                f'Deze instellingen passen niet in de gehele tijd, veranderen extra begin of eind tijd of gebruik een andere tijdsduur voor sloten.')
        return tijden

    @property
    def opbouw_minutes(self):
        return self.opstart_duur.seconds // 60

    @property
    def afbouw_minutes(self):
        return self.afbouw_duur.seconds // 60

    def clean(self):
        """
        Valideer dat het de gehele openingstijd gedefinieerd is.
        """
        if not(self.slot_tijden()[0][0] == self.open and self.slot_tijden()[-1][1] == self.sluit):
            raise ValidationError(
                f'Deze instellingen vullen niet de gehele tijd, veranderen extra begin of eind tijd of gebruik een andere tijdsduur voor sloten.')

    class Meta:
        verbose_name_plural = 'Schietdagen'


class Reservering(models.Model):
    """
    Een reservering is een tijdsduur op een baan.
    """
    start = models.DateTimeField()
    eind = models.DateTimeField()
    baan = models.ForeignKey(Baan, on_delete=models.CASCADE)
    schietdag = models.ForeignKey(Schietdag, on_delete=models.PROTECT)
    gebruiker = models.ForeignKey(User, on_delete=models.CASCADE)
    bonus = models.BooleanField(default=False)

    def __str__(self):
        return f"Reservering van {self.gebruiker.username} op {self.start}"

    @property
    def aankomst(self):
        return self.start - self.schietdag.opstart_duur

    @property
    def vertrek(self):
        return self.eind + self.schietdag.afbouw_duur

    @property
    def eerste_slot(self):
        current_tz = timezone.get_current_timezone()
        local_start = current_tz.normalize(self.start.astimezone(current_tz))
        return local_start.time() == datetime.datetime.combine(timezone.now(), self.schietdag.open).time()

    @property
    def laatste_slot(self):
        current_tz = timezone.get_current_timezone()
        local_eind = current_tz.normalize(self.eind.astimezone(current_tz))
        return local_eind.time() == datetime.datetime.combine(timezone.now(), self.schietdag.sluit).time()

    class Meta:
        verbose_name_plural = "Reserveringen"


class SiteConfiguration(SingletonModel):
    vereniging_naam = models.CharField(max_length=255, default='Eemschutters')
    reserveer_venster = models.DurationField(default=datetime.timedelta(
        7), help_text="Hoelang van te voren mogen sloten gereserveerd worden?")
    reserveringen_per_week = models.IntegerField(
        default=2, help_text="Hoeveel reserveringen per week mogen leden maken?")
    sleutelhouder_baan = models.ForeignKey(Baan, default=None, on_delete=models.SET_DEFAULT, null=True, blank=True,
                                           help_text="Op welke baan moet een sleutelhouders slot standaard gereserveerd worden?")
    sleutelhouder_slot = models.IntegerField(
        default=2, help_text="Op welk slot moeten een sleutehouders slot standaard gereserveerd worden? (eerste slot = 0)")

    def __str__(self):
        return "Instellingen"

    class Meta:
        verbose_name = "Instellingen"

class NieuwsBericht(models.Model):
    """
        Een nieuwsberichtje voor op de homepage
    """
    nieuws_bericht = models.TextField(
        max_length=800, default="Welkom, hier staat het laatste nieuws.", help_text="Een nieuwsberichtje op de homepagina.")
    gewijzigd_op = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Nieuwsbericht van {self.gewijzigd_op}"

    class Meta:
        verbose_name = "Nieuwsbericht"
        verbose_name_plural= "Nieuwsberichten"