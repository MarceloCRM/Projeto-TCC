from django.contrib import admin
from django.urls import path, include
from egresso.views import list_egresso, new_egresso

app_name = "egresso"

urlpatterns = [
    path('list_egresso/', list_egresso, name='list_egresso'),
    # path('new_egresso/', new_egresso, name='new_egresso'),

]