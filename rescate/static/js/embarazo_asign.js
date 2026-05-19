let embarazo = false;

document.getElementById('activar-formulario').addEventListener('dblclick', function() {
    var formulario = document.getElementById('form-embarazo');
    formulario.classList.toggle('d-none');

    embarazo = !embarazo;
    document.getElementById('input-embarazo').value = embarazo;
});

document.addEventListener('DOMContentLoaded', function () {
    const campoGestaciones = document.getElementById('id_numero_gestaciones');
    const formulario = document.getElementById('form-embarazo');
    const label = document.getElementById('activar-formulario');

    // Evita errores si algún elemento no existe
    if (!campoGestaciones || !formulario || !label) return;

    let testigos = false;

    if (campoGestaciones.value === '') {
        formulario.classList.add('d-none');
        label.classList.remove('d-none');
        testigos = false;
        if (typeof actualizarInputTestigos === 'function') {
            actualizarInputTestigos();
        }
    } else {
        formulario.classList.remove('d-none');
        label.classList.add('d-none');
        testigos = true;
    }
});

function validaFechasEmbarazo() {
    const fechaMenstruacion = document.querySelector('input[name="utlima_menstruacion"]');
    const fechaContracciones = document.querySelector('input[name="inicio_contracciones"]');
    const inputEmbarazo = document.querySelector('input[name="embarazo"]');

    // Comparamos el VALOR del input (.value)
    if (inputEmbarazo && inputEmbarazo.value === 'true') {
        
        const camposFecha = [
            { elemento: fechaMenstruacion, nombre: "Última Menstruación" },
            { elemento: fechaContracciones, nombre: "Inicio de Contracciones" }
        ];

        for (let campo of camposFecha) {
            // Si el campo no existe en el DOM o su valor está vacío
            if (!campo.elemento || !campo.elemento.value) {
                alert(`Por favor, complete la fecha y hora de: ${campo.nombre}`);
                if (campo.elemento) campo.elemento.focus();
                return false; // Detiene el flujo
            }
        }
    }

    return true; // Si no es 'true' o todo está lleno, permite continuar
}