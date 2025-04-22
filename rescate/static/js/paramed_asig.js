function moverASeleccionados(fila, clave, nombre) {
    const yaSeleccionado = document.querySelector(`#tabla-paramedicos-asignados tbody tr[data-clave="${clave}"]`);
    if (yaSeleccionado) return;

    const tablaAsignados = document.querySelector("#tabla-paramedicos-asignados tbody");
    const nuevaFila = tablaAsignados.insertRow();
    nuevaFila.setAttribute("data-clave", clave);

    nuevaFila.ondblclick = function () {
        moverAOriginales(this, clave, nombre);
    };

    const celdaClave = nuevaFila.insertCell(0);
    celdaClave.textContent = clave;

    const celdaNombre = nuevaFila.insertCell(1);
    celdaNombre.textContent = nombre;

    fila.remove();

    actualizarContador("tabla-paramedicos-disponibles", "contador-paramedicos-disponibles");
    actualizarContador("tabla-paramedicos-asignados", "contador-paramedicos-asignados");
}

function moverAOriginales(fila, clave, nombre) {
    const tablaDisponibles = document.querySelector("#tabla-paramedicos-disponibles tbody");
    const nuevaFila = tablaDisponibles.insertRow();
    nuevaFila.setAttribute("data-clave", clave);

    nuevaFila.ondblclick = function () {
        moverASeleccionados(this, clave, nombre);
    };

    const celdaClave = nuevaFila.insertCell(0);
    celdaClave.textContent = clave;

    const celdaNombre = nuevaFila.insertCell(1);
    celdaNombre.textContent = nombre;

    fila.remove();

    actualizarContador("tabla-paramedicos-disponibles", "contador-paramedicos-disponibles");
    actualizarContador("tabla-paramedicos-asignados", "contador-paramedicos-asignados");
}

function actualizarContador(idTabla, idContador) {
    const totalFilas = document.querySelectorAll(`#${idTabla} tbody tr:not(.d-none)`).length;
    document.getElementById(idContador).textContent = totalFilas;
}

document.addEventListener("DOMContentLoaded", function () {
    actualizarContador("tabla-paramedicos-disponibles", "contador-paramedicos-disponibles");
    actualizarContador("tabla-paramedicos-asignados", "contador-paramedicos-asignados");
});
