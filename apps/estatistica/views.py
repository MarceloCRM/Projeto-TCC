from django.shortcuts import render

def index(request):
    """
    Página inicial do app de estatística.
    """
    return render(request, 'estatistica/index.html')
