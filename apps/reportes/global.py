# reportes/global.py
from django.utils import timezone

def global_pdf_context(request):
    return {
        'user': 'Hector',  # nombre de usuario
        'now': timezone.now(),
        'clave': request.session.get('clave', ''),
        'permisos': request.session.get('permisos', []),
    }
