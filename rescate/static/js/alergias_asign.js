function moverASeleccionadosAlergia(fila, clave, nombre) {
    const yaSeleccionado = document.querySelector(`#tabla-alergias-asignadas tbody tr[data-nombre="${nombre}"]`);
    if (yaSeleccionado) return;

    const tablaAsignados = document.querySelector("#tabla-alergias-asignadas tbody");
    const nuevaFila = tablaAsignados.insertRow();
    nuevaFila.setAttribute("data-nombre", nombre);

    nuevaFila.ondblclick = function () {
        moverAOriginalesAlergia(this, clave, nombre);
    };

    //nuevaFila.insertCell(0).textContent = clave;

    nuevaFila.insertCell(0).textContent = clave;
    nuevaFila.insertCell(1).textContent = nombre;

    fila.remove();

    actualizarContador("tabla-alergias-disponibles", "contador-alergias-disponibles");
    actualizarContador("tabla-alergias-asignadas", "contador-alergias-asignadas");

    actualizarInputAlergias();
}

function actualizarInputAlergias() {
    const filas = document.querySelectorAll("#tabla-alergias-asignadas tbody tr");
    const paramedicos = [];

    filas.forEach(fila => {
        const clave = fila.cells[0].textContent.trim();
        const nombre = fila.cells[1].textContent.trim();
        paramedicos.push({ clave, nombre });
    });

    document.getElementById("input-alergias").value = JSON.stringify(paramedicos);
}

function eliminarSeleccionadosAlegias() {
    const asignados = document.querySelectorAll("#tabla-alergias-asignadas tbody tr");
    const disponibles = document.querySelector("#tabla-alergias-disponibles tbody");

    asignados.forEach(filaAsignado => {
        const claveAsignado = filaAsignado.cells[0]?.textContent.trim();

        const filasDisponibles = disponibles.querySelectorAll("tr");
        filasDisponibles.forEach(filaDisponible => {
            const claveDisponible = filaDisponible.cells[0]?.textContent.trim();
            if (claveDisponible === claveAsignado) {
                filaDisponible.remove();
            }
        });
    });

    actualizarContador("tabla-paramedicos-disponibles", "contador-paramedicos-disponibles");
}

function moverAOriginalesAlergia(fila, clave, nombre) {
    const tablaDisponibles = document.querySelector("#tabla-alergias-disponibles tbody");
    const nuevaFila = tablaDisponibles.insertRow();
    nuevaFila.setAttribute("data-clave", clave);

    nuevaFila.ondblclick = function () {
        moverASeleccionadosAlergia(this, clave, nombre);
    };

    const celdaClave = nuevaFila.insertCell(0);
    celdaClave.textContent = clave;

    const celdaNombre = nuevaFila.insertCell(1);
    celdaNombre.textContent = nombre;

    fila.remove();

    actualizarContador("tabla-alergias-disponibles", "contador-alergias-disponibles");
    actualizarContador("tabla-alergias-asignadas", "contador-alergias-asignadas");

    actualizarInputAlergias();
}

document.addEventListener("DOMContentLoaded", function () {
    actualizarInputAlergias();
    eliminarSeleccionadosAlegias();
    actualizarContador("tabla-alergias-disponibles", "contador-alergias-disponibles");
    actualizarContador("tabla-alergias-asignadas", "contador-alergias-asignadas");

    const filasAsignadas = document.querySelectorAll("#tabla-alergias-asignadas tbody tr");
    filasAsignadas.forEach(fila => {
        const clave = fila.cells[0]?.textContent.trim();
        const nombre = fila.cells[1]?.textContent.trim();

        fila.ondblclick = function () {
            moverAOriginalesAlergia(this, clave, nombre);
        };
    });
});
