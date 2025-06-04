from django.contrib import admin
from django.apps import apps

models = apps.get_models()  # Obtiene todos los modelos de la app
for model in models:
    try:
        admin.site.register(model)  # Intenta registrarlos
    except admin.sites.AlreadyRegistered:
        pass  # Si ya están registrados, los ignora
