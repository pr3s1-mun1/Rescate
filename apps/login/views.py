from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import logout
from apps.catalogos.models import Paramedicos, Logs_Sistema
from django.contrib.auth.hashers import check_password

def login_view(request):
    if request.method == "POST":
        usuario = request.POST.get("usuario", "").strip()
        contrasena = request.POST.get("contrasena", "").strip()

        if not usuario or not contrasena:
            messages.warning(request, "Por favor, completa todos los campos.")
            return render(request, "login.html")

        try:
            paramedico = Paramedicos.objects.get(usuario=usuario)

            if check_password(contrasena, paramedico.contrasena):
                request.session["clave"] = paramedico.clave
                request.session["user"] = paramedico.nombre
                request.session["permisos"] = paramedico.permisos

                Logs_Sistema.objects.create(
                    usuario=paramedico.nombre,
                    accion=f"Inició sesión"
                )

                return redirect("catalogo_general", "alergias")
            else:
                messages.error(request, "Usuario o contraseña incorrectos.")
        except Paramedicos.DoesNotExist:
            messages.error(request, "Usuario o contraseña incorrectos.")
        except Exception as e:
            messages.error(request, f"Ocurrió un error: {str(e)}")

    return render(request, "login.html")


def logout_view(request):
    usuario = request.session.get("user", "Desconocido")

    Logs_Sistema.objects.create(
        usuario=usuario,
        accion=f"Cerró sesión"
    )

    request.session.flush()
    return redirect('login')