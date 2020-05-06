from django.shortcuts import render, HttpResponse
from django.utils import timezone



# Create your views here.
def index(request):
    now = timezone.now()
    return HttpResponse(f"Hello, world. {now}.")