from django.shortcuts import render
from django.template.loader import get_template
from django.http import HttpResponse


def home(request):
    template = get_template("home.html")
    return HttpResponse(template.render({},request))

def problem(request):
    template = get_template("problem.html")
    return HttpResponse(template.render({},request))
# Create your views here.
