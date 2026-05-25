from django.contrib import admin

from .models import Demande, Domaine, Utilisateur

admin.site.register(Utilisateur)
admin.site.register(Domaine)
admin.site.register(Demande)
