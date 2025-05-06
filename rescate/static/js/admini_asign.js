function moverASeleccionadosAdministrado(row, clave, descripcion, unidad) {
    const yaSeleccionado = document.querySelector(`#tabla-administrado-asignado tbody tr[data-clave="${clave}"]`);
    if (yaSeleccionado) return;

    const nuevaFila = document.querySelector("#tabla-administrado-asignado tbody").insertRow();
    nuevaFila.setAttribute("data-clave", clave);

    nuevaFila.ondblclick = function () {
        moverADisponiblesAdministrado(nuevaFila, clave, descripcion, unidad);
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

    actualizarContador("tabla-administrado-disponible", "contador-administrado-disponible");
    actualizarContador("tabla-administrado-asignado", "contador-administrado-asignado");

    actualizarInputAdministrado();
}

function moverADisponiblesAdministrado(row, clave, descripcion, unidad) {
    const yaDisponible = document.querySelector(`#tabla-administrado-disponible tbody tr[data-clave="${clave}"]`);
    if (yaDisponible) return;

    const nuevaFila = document.querySelector("#tabla-administrado-disponible tbody").insertRow();
    nuevaFila.setAttribute("data-clave", clave);

    nuevaFila.ondblclick = function () {
        moverASeleccionadosAdministrado(nuevaFila, clave, descripcion, unidad);
    };

    nuevaFila.insertCell(0).textContent = clave;
    nuevaFila.insertCell(1).textContent = descripcion;
    const celdaUnidad = nuevaFila.insertCell(2);
    celdaUnidad.textContent = unidad;
    celdaUnidad.hidden = true;

    row.remove();

    actualizarContador("tabla-administrado-disponible", "contador-administrado-disponible");
    actualizarContador("tabla-administrado-asignado", "contador-administrado-asignado");

    actualizarInputAdministrado();
}

function actualizarInputAdministrado() {
    const filas = document.querySelectorAll("#tabla-administrado-asignado tbody tr");
    const administrados = [];

    filas.forEach(fila => {
        const clave = fila.cells[0].textContent.trim();
        const descripcion = fila.cells[1].textContent.trim();
        const unidad = fila.cells[2].textContent.trim();
        const cantidad = fila.cells[3].querySelector("input")?.value || "0";
        administrados.push({ clave, descripcion, unidad, cantidad });
    });

    document.getElementById("input-administrado").value = JSON.stringify(administrados);
}

function eliminarSeleccionadosAdministrado() {
    const asignados = document.querySelectorAll("#tabla-administrado-asignado tbody tr");
    const disponibles = document.querySelector("#tabla-administrado-disponible tbody");

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

    actualizarContador("tabla-administrado-disponible", "contador-administrado-disponible");
}

document.addEventListener("DOMContentLoaded", function () {
    actualizarInputAdministrado();
    eliminarSeleccionadosAdministrado();
    actualizarContador("tabla-administrado-disponible", "contador-administrado-disponible");
    actualizarContador("tabla-administrado-asignado", "contador-administrado-asignado");
});
