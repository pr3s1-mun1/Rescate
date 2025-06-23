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
