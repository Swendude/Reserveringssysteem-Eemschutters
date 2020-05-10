from django import forms
from .models import Reservering, Baan, Schietdag
from django.forms import ModelForm


class ReserveringForm(forms.Form):
    start = forms.DateTimeField(widget=forms.HiddenInput())
    eind = forms.DateTimeField(widget=forms.HiddenInput())
    baan = forms.ModelChoiceField(Baan.objects.all(), widget=forms.HiddenInput())
    schietdag = forms.ModelChoiceField(Schietdag.objects.all(), widget=forms.HiddenInput())

# class DeleteReserveringForm(forms.Form):
#     id = forms.