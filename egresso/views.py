from django.shortcuts import render
from egresso.models import Egresso

def list_egresso(request):
    egresso = Egresso.objects.all()
    template_name = "list_egresso.html"
    context = {
        "egresso": egresso
    }
    return render(request, template_name, context)