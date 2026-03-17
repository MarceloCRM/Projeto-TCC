from django.shortcuts import redirect, render
from apps.egresso.forms import EgressoForm
from apps.egresso.models import Egresso

def listar_egresso(request):
    egresso = Egresso.objects.all()
    template_name = "listar_egresso.html"
    context = {
        "egresso": egresso
    }
    return render(request, template_name, context)

def new_egresso(request):
    if request.method == "POST":
        form = EgressoForm(request.POST)
        print(form.errors)
        if form.is_valid():
            form.save()
            return redirect('egresso:list_egresso')
    else:
        return render(request, template_name="new_egresso.html", context={"form": EgressoForm()})