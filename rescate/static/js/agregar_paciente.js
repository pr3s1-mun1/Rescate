// ✅ Lista de servicios que permiten guardar sin paciente
const salidasFalsos = [34, 35, 213];

// ✅ IDs de pestañas que se deben desactivar si se guarda sin paciente
const pestanasInactivas = [
    "paciente-tab", "pertenencias-tab", "embarazo-tab", "procedimientos-tab",
    "alergia-tab", "material-tab", "ingerido-tab", "administrado-tab",
    "equipo-tab", "lesion-tab", "procedimiento-tab", "impacto-tab",
    "quemadura-tab", "testigo-tab"
];

document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('servicioForm');
    const campoServicio = document.getElementById("id_tipo_servicio_realizado");
    const btnGuardar = document.getElementById('btnGuardar');
    const btnGuardarSinPaciente = document.getElementById('btnGuardarSinPaciente');

    if (!form || !campoServicio || !btnGuardar || !btnGuardarSinPaciente) return;

    // 🔹 Estado inicial: ocultar botón sin paciente
    btnGuardarSinPaciente.style.display = 'none';


    // Función que aplica el estado de los botones y pestañas
    function actualizarUI() {
        const valor = parseInt(campoServicio.value, 10);
        const esSalidaFalsa = salidasFalsos.includes(valor);

        btnGuardarSinPaciente.style.display = esSalidaFalsa ? 'inline-block' : 'none';
        btnGuardar.style.display = esSalidaFalsa ? 'none' : 'inline-block';

        pestanasInactivas.forEach(id => {
            const pestana = document.getElementById(id);
            if (pestana) pestana.style.display = esSalidaFalsa ? 'none' : 'inline-block';
        });
    }

    actualizarUI();

    campoServicio.addEventListener("change", actualizarUI);

    function validarYEnviar(e, sinPaciente=false) {
        let pestañasAValidar = [
            'servicio', 'unidad', 'paramedicos', 'paciente', 'procedimiento', 'alergia',
            'material', 'ingerido', 'administrado', 'equipo', 'lesion', 'impacto', 'partes'
        ];

        let pestanasIgnorar = sinPaciente ? [
            'paciente', 'procedimiento', 'alergia', 'material', 'ingerido',
            'administrado', 'equipo', 'lesion', 'impacto', 'partes'
        ] : [];

        let todoValido = true;

        for (const tabId of pestañasAValidar) {
            if (pestanasIgnorar.includes(tabId)) continue;

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

        // Deshabilitar botones mientras se guarda
        if (sinPaciente) {
            btnGuardarSinPaciente.disabled = true;
            btnGuardarSinPaciente.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i> Guardando sin paciente...';
            form.action = btnGuardarSinPaciente.dataset.url;
        } else {
            btnGuardar.disabled = true;
            btnGuardar.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i> Guardando...';
        }

        return true;
    }

    // 🔹 Submit normal
    form.addEventListener('submit', function(e){
        return validarYEnviar(e, false);
    });

    // 🔹 Guardar sin paciente
    btnGuardarSinPaciente.addEventListener('click', function(e){
        e.preventDefault();
        if (confirm("¿Está seguro que desea guardar este servicio sin paciente?")) {
            // Asignar la URL correcta al formulario
            form.action = btnGuardarSinPaciente.dataset.url;
            form.submit();
        }
    });


    // 🔹 Función de validación de cada pestaña
    function validarPestana(tabId) {
        const tab = document.getElementById(tabId);
        if (!tab) return true; // Si no existe, no bloquea

        let isValid = true;

        // Validar campos requeridos
        const requiredFields = tab.querySelectorAll('[required]');
        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                field.classList.add('is-invalid');
                isValid = false;
            } else {
                field.classList.remove('is-invalid');
            }
        });

        // Validaciones especiales de tablas
        const tablas = {
            'unidad': '#tabla-seleccionados tbody tr',
            'paramedicos': '#tabla-paramedicos-asignados tbody tr',
            'procedimiento': '#tabla-procedimientos-asignados tbody tr',
            'alergia': '#tabla-alergias-asignadas tbody tr',
            'material': '#tabla-materiales-asignados tbody tr',
            'ingerido': '#tabla-ingerido-asignado tbody tr',
            'administrado': '#tabla-administrado-asignado tbody tr',
            'equipo': '#tabla-equipo-asignado tbody tr'
        };

        if (tablas[tabId]) {
            const rows = document.querySelectorAll(tablas[tabId]);
            if (rows.length === 0) {
                alert(`Debe agregar al menos un elemento en la pestaña "${tabId}".`);
                isValid = false;
            }
        }

        actualizarInputs();
        return isValid;
    }

    // 🔹 Funciones auxiliares
    function actualizarInputs(){
        actualizarInputAdministrado();
        actualizarInputEquipo(); 
        actualizarInputIngerido();
        actualizarInputMateriales();
        llenarInputs();
    }

    // 🔹 Eliminación de filas con doble click
    function habilitarEliminacionPorDobleClick(idTabla) {
        const tabla = document.getElementById(idTabla);
        if (!tabla) return;

        tabla.addEventListener('dblclick', function (e) {
            const fila = e.target.closest('tr');
            if (fila) {
                fila.remove();
                actualizarInputs();
                actualizarContador("tabla-seleccionados", "contados-unidades");
            }
        });
    }

    // 🔹 Confirmaciones
    window.confirmarGuardar = function() {
        return confirm("¿Estás seguro de que deseas guardar los cambios?");
    }

    window.confirmarCancelar = function() {
        return confirm("¿Estás seguro de que desea cancelar el agregado del paciente?");
    }
});
