from django.shortcuts import render
from apps.catalogos.views import requiere_sesion

# Create your views here.
@requiere_sesion
def manual_home(request):
    return render(request, 'manual.html')