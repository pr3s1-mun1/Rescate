// Navegación entre pestañas
document.querySelectorAll('.next-tab').forEach(button => {
    button.addEventListener('click', function () {
        const nextTabId = this.getAttribute('data-next-tab');
        const nextTab = document.getElementById(nextTabId);
        const tabInstance = new bootstrap.Tab(nextTab);
        tabInstance.show();
    });
});

document.querySelectorAll('.prev-tab').forEach(button => {
    button.addEventListener('click', function () {
        const prevTabId = this.getAttribute('data-prev-tab');
        const prevTab = document.getElementById(prevTabId);
        const tabInstance = new bootstrap.Tab(prevTab);
        tabInstance.show();
    });
});

document.addEventListener('DOMContentLoaded', function () {
    const pestañasAValidar = ['servicio', 'unidad', 'paramedicos', 'paciente', 'embarazo', 'procedimiento', 'alergia', 'material', 'ingerido', 'administrado', 'equipo', 'lesion', 'impacto'];

    document.getElementById('servicioForm').addEventListener('submit', function (e) {
        let todoValido = true;

        for (const tabId of pestañasAValidar) {
            const resultado = validarPestana(tabId);
            if (!resultado) {
                todoValido = false;

                // Cambiar a la pestaña con error y salir del loop
                const tabButton = document.querySelector(`button[data-bs-target="#${tabId}"]`);
                if (tabButton) {
                    const tab = new bootstrap.Tab(tabButton);
                    tab.show();
                }

                break;
            }
        }

        if (!todoValido) {
            e.preventDefault();
            alert('Por favor complete todos los campos requeridos.');
            return false;
        }

        // Deshabilitar botón
        const submitBtn = document.getElementById('btnGuardar');
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i> Guardando...';

        return true;
    });
});


function validarPestana(tabId) {
    console.log(`Validando pestaña: ${tabId}`);
    let isValid = true;
    const tab = document.getElementById(tabId);

    if (!tab) {
        console.warn(`No se encontró la pestaña con ID: ${tabId}`);
        return true; // No bloquear si no existe
    }

    // Validar todos los campos requeridos en la pestaña
    const requiredFields = tab.querySelectorAll('[required]');
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.classList.add('is-invalid');
            isValid = false;
        } else {
            field.classList.remove('is-invalid');
        }
    });

    // Validaciones de tablas con input
    if (tabId === 'unidad') {
        const rows = document.querySelectorAll('#tabla-seleccionados tbody tr');
        if (rows.length === 0) {
            alert('Debe agregar al menos una unidad');
            isValid = false;
        } else {
            for (const row of rows) {
                const inputs = row.querySelectorAll('input');
                for (const input of inputs) {
                    if (!input.value.trim()) {
                        alert('Todos los campos en las filas deben estar llenos.');
                        isValid = false;
                        break;
                    }
                }
                if (!isValid) break;
            }
        }
    }  

    // Validaciones de tablas
    if (tabId === 'paramedicos') {
        const rows = document.querySelectorAll('#tabla-paramedicos-asignados tbody tr');
        if (rows.length === 0) {
            alert('Debe agregar al menos un paramédico.');
            isValid = false;
        }
    }

    if (tabId === 'procedimiento') {
        const rows = document.querySelectorAll('#tabla-procedimientos-asignados tbody tr');
        if (rows.length === 0) {
            alert('Debe agregar al menos un procedimiento.');
            isValid = false;
        }
    }

    if (tabId === 'alergia') {
        const rows = document.querySelectorAll('#tabla-alergias-asignadas tbody tr');
        if (rows.length === 0) {
            alert('Debe agregar al menos una alergía.');
            isValid = false;
        }
    }

    if (tabId === 'material') {
        const rows = document.querySelectorAll('#tabla-materiales-asignados tbody tr');
        if (rows.length === 0) {
            alert('Debe agregar al menos un material.');
            isValid = false;
        }
    }

    if (tabId === 'ingerido') {
        const rows = document.querySelectorAll('#tabla-ingerido-asignado tbody tr');
        if (rows.length === 0) {
            alert('Debe agregar al menos un ingerido.');
            isValid = false;
        }
    }

    if (tabId === 'administrado') {
        const rows = document.querySelectorAll('#tabla-administrado-asignado tbody tr');
        if (rows.length === 0) {
            alert('Debe agregar al menos un administrado.');
            isValid = false;
        }
    }

    if (tabId === 'equipo') {
        const rows = document.querySelectorAll('#tabla-equipo-asignado tbody tr');
        if (rows.length === 0) {
            alert('Debe agregar al menos un equipo.');
            isValid = false;
        }
    }

    if (tabId === 'lesion') {
        const rows = document.querySelectorAll('#tabla-partes-seleccionadas tbody tr');
        if (rows.length === 0) {
            alert('Debe agregar al menos una lesión.');
            isValid = false;
        }
    }

    if (tabId === 'impacto') {
        const rows = document.querySelectorAll('#tabla-impacto-seleccionadas tbody tr');
        if (rows.length === 0) {
            alert('Debe agregar al menos un impacto.');
            isValid = false;
        }
    }

    return isValid;
}
