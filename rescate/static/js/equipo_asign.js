function moverASeleccionadosequipo(row, clave, descripcion, unidad) {
    const yaSeleccionado = document.querySelector(`#tabla-equipo-asignado tbody tr[data-clave="${clave}"]`);
    if (yaSeleccionado) return;

    const nuevaFila = document.querySelector("#tabla-equipo-asignado tbody").insertRow();
    nuevaFila.setAttribute("data-clave", clave);

    nuevaFila.ondblclick = function () {
        moverADisponiblesequipo(nuevaFila, clave, descripcion, unidad);
    };

    const celdaClave = nuevaFila.insertCell(0);
    celdaClave.textContent = clave;
    celdaClave.hidden = true;

    nuevaFila.insertCell(1).textContent = descripcion;
    nuevaFila.insertCell(2).textContent = unidad;

    const celdaCantidad = nuevaFila.insertCell(3);
    const inputCantidad = document.createElement("input");
    inputCantidad.type = "number";
    inputCantidad.className = "form-control";
    inputCantidad.value = "1";
    celdaCantidad.appendChild(inputCantidad);

    row.remove();

    actualizarContador("tabla-equipo-disponible", "contador-equipo-disponible");
    actualizarContador("tabla-equipo-asignado", "contador-equipo-asignado");

    actualizarInputEquipo();
}

function moverADisponiblesequipo(row, clave, descripcion, unidad) {
    const yaDisponible = document.querySelector(`#tabla-equipo-disponible tbody tr[data-clave="${clave}"]`);
    if (yaDisponible) return;

    const nuevaFila = document.querySelector("#tabla-equipo-disponible tbody").insertRow();
    nuevaFila.setAttribute("data-clave", clave);

    nuevaFila.ondblclick = function () {
        moverASeleccionadosequipo(nuevaFila, clave, descripcion, unidad);
    };

    nuevaFila.insertCell(0).textContent = clave;
    nuevaFila.insertCell(1).textContent = descripcion;
    const celdaUnidad = nuevaFila.insertCell(2);
    celdaUnidad.textContent = unidad;
    celdaUnidad.hidden = true;

    row.remove();

    actualizarContador("tabla-equipo-disponible", "contador-equipo-disponible");
    actualizarContador("tabla-equipo-asignado", "contador-equipo-asignado");

    actualizarInputEquipo();
}

function actualizarInputEquipo() {
    const filas = document.querySelectorAll("#tabla-equipo-asignado tbody tr");
    const equipo = [];

    filas.forEach(fila => {
        const clave = fila.cells[0].textContent.trim();
        const descripcion = fila.cells[1].textContent.trim();
        const unidad = fila.cells[2].textContent.trim();
        const cantidad = fila.cells[3].querySelector("input")?.value || "0";
        equipo.push({ clave, descripcion, unidad, cantidad });
    });

    document.getElementById("input-equipo").value = JSON.stringify(equipo);
}

function eliminarSeleccionadosEquipo() {
    const asignados = document.querySelectorAll("#tabla-equipo-asignado tbody tr");
    const disponibles = document.querySelector("#tabla-equipo-disponible tbody");

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

    actualizarContador("tabla-equipo-disponible", "contador-equipo-disponible");
}

document.addEventListener("DOMContentLoaded", () => {
    actualizarInputEquipo();
    eliminarSeleccionadosEquipo();
    actualizarContador("tabla-equipo-disponible", "contador-equipo-disponible");
    actualizarContador("tabla-equipo-asignado", "contador-equipo-asignado");

    const filasAsignadasEqui = document.querySelectorAll("#tabla-equipo-asignado tbody tr");
    filasAsignadasEqui.forEach(fila => {
        const clave = fila.cells[0]?.textContent.trim();
        const nombre = fila.cells[1]?.textContent.trim();
        const unidad = fila.cells[2]?.textContent.trim();
        fila.ondblclick = function () {
            moverADisponiblesequipo(this, clave, nombre, unidad);
        };
    });
});
