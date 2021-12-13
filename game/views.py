from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render


def index(request):
    context = {}
    return render(request, 'game/index.html', context)
