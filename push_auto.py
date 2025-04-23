import os
import sys

def git_auto_push():
    # Solicitar mensaje del commit
    commit_message = input("Ingresa el mensaje del commit: ").strip()
    if not commit_message:
        print("❌ El mensaje del commit no puede estar vacío.")
        sys.exit(1)

    # Solicitar nombre de la rama (opcional, por defecto 'main')
    branch_name = input("Ingresa el nombre de la rama (default: main): ").strip()
    if not branch_name:
        branch_name = "main"

    # Comandos Git
    commands = [
        "git add .",
        f'git commit -m "{commit_message}"',
        f"git push origin {branch_name}"
    ]

    # Ejecutar comandos
    for cmd in commands:
        print(f"\nEjecutando: {cmd}")
        exit_code = os.system(cmd)
        if exit_code != 0:
            print(f"❌ Error al ejecutar: {cmd}")
            sys.exit(1)

    print("\n✅ ¡Push completado con éxito!")

if __name__ == "__main__":
    git_auto_push()