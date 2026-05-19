document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('servicioForm');

    form.addEventListener('submit', function (e) {
        // Validar pestañas (JS)
        let pestañasAValidar = ['servicio', 'unidad', 'paramedicos', 'paciente', 'procedimiento', 'alergia', 'material', 'ingerido', 'administrado', 'equipo', 'lesion', 'impacto', 'partes'];
        let pestanasIgnorar = ['procedimiento', 'alergia', 'material', 'ingerido', 'administrado', 'equipo', 'lesion', 'impacto', 'partes', 'paciente']


        let todoValido = true;

        for (const tabId of pestañasAValidar) {
            const resultado = validarPestana(tabId);
            if (!resultado) {
                todoValido = false;

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

        if (!validaFechasEmbarazo()){
            e.preventDefault();
            alert('Los campos de fechas en embarazo no están completos, favor de verificar')
            return false;
        }

        // Deshabilitar el botón de submit mientras se guarda
        const submitBtn = document.getElementById('btnGuardar');
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i> Guardando...';
        }

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

    actualizarInputs();
    return isValid;
}

function actualizarInputs(){
    actualizarInputAdministrado();
    actualizarInputEquipo(); 
    actualizarInputIngerido();
    actualizarInputMateriales();
    actualizarInputIngerido();
    llenarInputs()
}

function habilitarEliminacionPorDobleClick(idTabla) {
    const tabla = document.getElementById(idTabla);

    if (!tabla) {
        console.warn(`No se encontró una tabla con el ID "${idTabla}".`);
        return;
    }

    tabla.addEventListener('dblclick', function (e) {
        const fila = e.target.closest('tr');

        // Evita eliminar si es encabezado
        if (fila ) {
                fila.remove();
                actualizarInputs();
                actualizarContador("tabla-seleccionados", "contados-unidades");
        }
    });
}

function confirmarGuardar() {
    return confirm("¿Estás seguro de que deseas guardar los cambios?");
}

function confirmarCancelar() {
    return confirm("¿Estás seguro de que desea cancelar el agregado del paciente?");
}

