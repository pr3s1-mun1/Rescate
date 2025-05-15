let embarazo = false;

document.getElementById('activar-formulario').addEventListener('dblclick', function() {
    var formulario = document.getElementById('form-embarazo');
    formulario.classList.toggle('d-none');

    embarazo = !embarazo;
    document.getElementById('input-embarazo').value = embarazo;
});