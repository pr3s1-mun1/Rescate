function agregarTestigo() {
    const nombre = document.getElementById('nomtestigo').value.trim();
    const edad = document.getElementById('edad').value.trim(); // ¡Corregido!
    const direccion = document.getElementById('direccion').value.trim();
    const telefono = document.getElementById('telefono').value.trim(); // ¡Corregido!
    const parentesco = document.getElementById('parentesco').value.trim();

    if (!nombre || !edad || !direccion || !telefono || !parentesco) {
        alert("Por favor, completa todos los campos.");
        return;
    }

    const tabla = document.getElementById('tabla-testigos');
    const fila = document.createElement('tr');

    fila.innerHTML = `
        <td>${nombre}</td>
        <td>${edad}</td>
        <td>${direccion}</td>
        <td>${telefono}</td>
        <td>${parentesco}</td>
        <td><button type="button" class="btn-action eliminar-fila"><i class="bi bi-trash-fill"></i></button></td>
    `;

    tabla.appendChild(fila);

    // Limpiar campos
    document.getElementById('nomtestigo').value = '';
    document.getElementById('edad').value = ''; // ¡Corregido!
    document.getElementById('direccion').value = '';
    document.getElementById('telefono').value = '';

    actualizarInputTestigos();
}

// Variable para controlar visibilidad (opcional, pero mejor derivar del DOM)
let testigosActivos = false;

document.getElementById('activar-testigos').addEventListener('dblclick', function() {
    const formulario = document.getElementById('form-testigos');
    formulario.classList.toggle('d-none');
    const label = document.getElementById('activar-testigos');
    label.classList.toggle('d-none'); // ¿Quieres ocultar la etiqueta al activar?

    testigosActivos = !testigosActivos;
    document.getElementById('input-testigos').value = testigosActivos;
});

function actualizarInputTestigos() {
    const tabla = document.getElementById('tabla-testigos');
    const filas = tabla.querySelectorAll('tr');
    const testigos = [];

    filas.forEach(fila => {
        const columnas = fila.querySelectorAll('td');
        if (columnas.length >= 5) { // al menos 5 columnas de datos
            const testigo = {
                nombre: columnas[0].textContent.trim(),
                edad: columnas[1].textContent.trim(),
                direccion: columnas[2].textContent.trim(),
                telefono: columnas[3].textContent.trim(),
                parentesco: columnas[4].textContent.trim(),
            };
            testigos.push(testigo);
        }
    });

    document.getElementById('input-testigos').value = JSON.stringify(testigos);
}

function conteoTabla(idTabla) {
    const tabla = document.getElementById(idTabla);
    return tabla.querySelectorAll('tr').length > 0;
}

document.addEventListener('DOMContentLoaded', function () {
    const tieneTestigos = conteoTabla('tabla-testigos');
    const formulario = document.getElementById('form-testigos');
    const label = document.getElementById('activar-testigos');

    if (tieneTestigos) {
        formulario.classList.remove('d-none');
        label.classList.add('d-none'); // o quitar si no quieres ocultarlo
        actualizarInputTestigos();
    }

    // Evento delegado para eliminar
    document.getElementById('tabla-testigos').addEventListener('click', function(e) {
        if (e.target.closest('.eliminar-fila')) {
            const fila = e.target.closest('tr');
            if (fila) {
                fila.remove();
                if (!conteoTabla('tabla-testigos')) {
                    formulario.classList.add('d-none');
                    label.classList.remove('d-none');
                }
                actualizarInputTestigos();
            }
        }
    });
});