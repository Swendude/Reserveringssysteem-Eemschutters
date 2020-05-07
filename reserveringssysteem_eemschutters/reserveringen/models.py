from django.db import models
from django.contrib.auth.models import User
import datetime
from django.core.exceptions import ValidationError
from multiselectfield import MultiSelectField


class Baan(models.Model):
    naam = models.CharField(max_length=50)
    mobiel = models.BooleanField()
    afstand = models.IntegerField(help_text='in meters')

    def __str__(self):
        if not self.mobiel:
            return f"Baan: {self.naam} ({self.afstand} m)"
        else:
            return f"Baan: {self.naam} (mobiel)"

    class Meta:
        verbose_name_plural = "Banen"


DAGEN = ((0, 'Maandag'),
         (1, 'Dinsdag'),
         (2, 'Woensdag'),
         (3, 'Donderdag'),
         (4, 'Vrijdag'),
         (5, 'Zaterdag'),
         (6, 'Zondag'))


class Protocol(models.Model):
    """
    Een protocol is een instelling waarmee een reserveringen gemaakt kan worden.
    """
    slot_duur = models.DurationField()
    opstart_duur = models.DurationField()
    afbouw_duur = models.DurationField()
    open = models.TimeField()
    sluit = models.TimeField()
    prioriteit = models.IntegerField()
    geldig_op = MultiSelectField(choices=DAGEN, default=None, null=True, blank=True)

    def __str__(self):
        return f'Protocol {self.prioriteit}'

    @property
    def aantal_slots(self):
        """
        Bereken het aantal slots als gevolg van dit protocol.
        """
        tijd_open = datetime.timedelta(hours=self.sluit.hour - self.open.hour,
                                       minutes=self.sluit.minute - self.open.minute)

        return tijd_open/self.slot_duur
    
    @property
    def dagen(self):
        return dict(DAGEN)

    def clean(self):
        """
        Valideer dat het aantal slots een rond getal is.
        """
        if not self.aantal_slots.is_integer():
            raise ValidationError(
                f'Er zijn {self.aantal_slots} slots in dit protocol. Dit moet een rond getal zijn.')

    class Meta:
        verbose_name_plural = 'Protocollen'
        


class Reservering(models.Model):
    """
    Een reservering is een tijdsduur op een baan. 
    Dit object kan alleen aangemaakt worden vanuit een protocol.
    """
    start = models.DateTimeField()
    eind = models.DateTimeField()
    baan = models.ForeignKey(Baan, on_delete=models.PROTECT)
    protocol = models.ForeignKey(Protocol, on_delete=models.PROTECT)
    gebruiker = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Reservering van {self.gebruiker.username} op {self.start}"

    class Meta:
        verbose_name_plural = "Reserveringen"
