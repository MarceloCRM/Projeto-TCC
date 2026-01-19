from django.contrib import admin
from .models import Egresso

@admin.register(Egresso)
class EgressoAdmin(admin.ModelAdmin):
    list_display = (
        'fullName',
        'birthDate',
        'gender',
        'status',
        'email',
        'number',
    )

    search_fields = (
        'fullName',
        'email',
        'number',
    )

    list_filter = (
        'gender',
        'status',
    )

    ordering = ('fullName',)
