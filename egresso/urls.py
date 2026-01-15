from django.contrib import admin
from django.urls import path, include
from egresso.views import list_egresso

app_name = "egresso"

urlpatterns = [
    path('list_egresso', list_egresso, name='list_egresso')
]