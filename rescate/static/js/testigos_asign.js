function agregarTestigo() {
    const nombre = document.getElementById('nomtestigo').value.trim();
    const edad = document.getElementById('telefono').value.trim();
    const direccion = document.getElementById('direccion').value.trim();
    const numero = document.getElementById('numero').value.trim();

    if (!nombre || !edad || !direccion || !numero) {
        alert("Por favor, completa todos los campos.");
        return;
    }

    const tabla = document.getElementById('tabla-testigos');
    const fila = document.createElement('tr');

    fila.innerHTML = `
        <td>${nombre}</td>
        <td>${edad}</td>
        <td>${direccion}</td>
        <td>${numero}</td>
        <td><button type="button" class="btn btn-danger btn-sm eliminar-fila">Eliminar</button></td>
    `;

    tabla.appendChild(fila);

    fila.querySelector('.eliminar-fila').addEventListener('click', function () {
        fila.remove();
        actualizarInputTestigos
    });


    // Limpiar campos
    document.getElementById('nomtestigo').value = '';
    document.getElementById('telefono').value = '';
    document.getElementById('direccion').value = '';
    document.getElementById('numero').value = '';

    actualizarInputTestigos();
}

let testigos = false;

document.getElementById('activar-testigos').addEventListener('dblclick', function() {
    var formulario = document.getElementById('form-testigos');
    formulario.classList.toggle('d-none');

    testigos = !testigos;
    document.getElementById('input-testigos').value = testigos;
});

function actualizarInputTestigos() {
    const tabla = document.getElementById('tabla-testigos');
    const filas = tabla.querySelectorAll('tr');
    const testigos = [];

    filas.forEach(fila => {
        const columnas = fila.querySelectorAll('td');
        if (columnas.length === 5) {
            const testigo = {
                nombre: columnas[0].textContent.trim(),
                edad: columnas[1].textContent.trim(),
                direccion: columnas[2].textContent.trim(),
                telefono: columnas[3].textContent.trim(),

            };
            testigos.push(testigo);
        }
    });

    // Guarda como JSON en input hidden
    document.getElementById('input-testigos').value = JSON.stringify(testigos);
}


function conteoTabla(idTabla) {
    const tabla = document.getElementById(idTabla);
    const filas = tabla.querySelectorAll('tr');
    return filas.length > 0;

}

document.addEventListener('DOMContentLoaded', function () {
    if(conteoTabla('tabla-testigos')) {
        var formulario = document.getElementById('form-testigos');
        formulario.classList.toggle('d-none');
        testigos = !testigos;
        var label = document.getElementById('activar-testigos');
        label.classList.toggle('d-none');
        actualizarInputTestigos();
    }

    document.getElementById('tabla-testigos').addEventListener('click', function(e) {
        if (e.target && e.target.classList.contains('eliminar-fila')) {
            const fila = e.target.closest('tr');
            fila.remove();

            if (!conteoTabla('tabla-testigos')) {
                var formulario = document.getElementById('form-testigos');
                formulario.classList.toggle('d-none');
                testigos = !testigos;
            }
        }
        actualizarInputTestigos()
    });
});