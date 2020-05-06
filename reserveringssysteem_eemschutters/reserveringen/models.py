from django.db import models
from django.contrib.auth.models import User
import datetime


class Baan(models.Model):
    naam = models.CharField(max_length=50)
    mobiel = models.BooleanField()
    afstand = models.IntegerField(help_text='in meters')

    def __str__(self):
        if not self.mobiel:
            return f"Baan: {self.naam} ({self.afstand} m)"
        else:
            return f"Mobiele baan: {self.naam}"

    class Meta:
        verbose_name_plural = "Banen"


class Protocol(models.Model):
    """
    Een protocol is een instelling waarmee een Slot gemaakt kan worden.
    """
    slot_duur = models.DurationField()
    opstart_duur = models.DurationField()
    afbouw_duur = models.DurationField()
    open = models.TimeField()
    sluit = models.TimeField()
    prioriteit = models.IntegerField()

    def __str__(self):
        return f"Protocol {self.prioriteit}"

    @property
    def aantal_slots(self):
        tijd_open = datetime.timedelta(hours=self.sluit.hour - self.open.hour,
                                       minutes=self.sluit.minute - self.open.minute)

        return tijd_open/self.slot_duur

    class Meta:
        verbose_name_plural = "Protocollen"

# class Slot(models.Model):
#     datum = models.DateField()
#     start =

# class Question(models.Model):
#     question_text = models.CharField(max_length=200)
#     pub_date = models.DateTimeField('date published')


# class Choice(models.Model):
#     question = models.ForeignKey(Question, on_delete=models.CASCADE)
#     choice_text = models.CharField(max_length=200)
#     votes = models.IntegerField(default=0)
