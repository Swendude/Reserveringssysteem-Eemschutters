from django.shortcuts import render, HttpResponse
from django.utils import timezone



# Create your views here.
def index(request):
    return render(request, 'reserveringen/reserveringen.html', {})