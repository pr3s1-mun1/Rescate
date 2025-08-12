from django.shortcuts import render

# Create your views here.

def manual_home(request):
    return render(request, 'manual.html')