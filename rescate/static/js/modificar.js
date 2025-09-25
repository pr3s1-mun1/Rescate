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
    const form = document.getElementById('servicioForm');
    const selectTipo = document.getElementById('id_tipo_servicio_realizado');

    const comisiones = ['245','197','213','138','247','248','38','198','227','223','224','172','222','196','211','204','180','210','186','241','218', '34', '35']

    form.addEventListener('submit', function (e) {
        // Saltar validaciones si se selecciona un valor específico
        if (comisiones.includes(selectTipo.value)) { 
            return true; // permite enviar el formulario sin validar las pestañas
        }

        // Validación normal de pestañas
        const pestañasAValidar = ['servicio', 'unidad', 'paramedicos', 'procedimiento', 'alergia', 'material', 'ingerido', 'administrado', 'equipo', 'lesion', 'impacto', 'partes'];
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

        // Deshabilitar botón de submit mientras se guarda
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
