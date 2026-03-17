from django.shortcuts import render, get_object_or_404
from apps.egresso.models import Egresso
from apps.formularios.models import Formulario

def index(request):
    egressos = Egresso.objects.all()
    total_egre = egressos.count()

    formulario = Formulario.objects.all()
    total_form = formulario.count()

    template_name = "index.html"
    context = {
        "egresso_total" : total_egre,
        "formulario_total" : total_form
        
    }
    return render(request, template_name, context)
