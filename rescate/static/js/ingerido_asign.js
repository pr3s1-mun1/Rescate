function moverASeleccionadosIngerido(row, clave, descripcion, unidad) {
    const yaSeleccionado = document.querySelector(`#tabla-ingerido-asignado tbody tr[data-clave="${clave}"]`);
    if (yaSeleccionado) return;

    const nuevaFila = document.querySelector("#tabla-ingerido-asignado tbody").insertRow();
    nuevaFila.setAttribute("data-clave", clave);

    nuevaFila.ondblclick = function () {
        moverADisponiblesIngerido(nuevaFila, clave, descripcion, unidad);
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

    actualizarContador("tabla-ingerido-disponible", "contador-ingerido-disponible");
    actualizarContador("tabla-ingerido-asignado", "contador-ingerido-asignado");

    actualizarInputIngerido();
}

function moverADisponiblesIngerido(row, clave, descripcion, unidad) {
    const yaDisponible = document.querySelector(`#tabla-ingerido-disponible tbody tr[data-clave="${clave}"]`);
    if (yaDisponible) return;

    const nuevaFila = document.querySelector("#tabla-ingerido-disponible tbody").insertRow();
    nuevaFila.setAttribute("data-clave", clave);

    nuevaFila.ondblclick = function () {
        moverASeleccionadosIngerido(nuevaFila, clave, descripcion, unidad);
    };

    nuevaFila.insertCell(0).textContent = clave;
    nuevaFila.insertCell(1).textContent = descripcion;
    const celdaUnidad = nuevaFila.insertCell(2);
    celdaUnidad.textContent = unidad;
    celdaUnidad.hidden = true;

    row.remove();

    actualizarContador("tabla-ingerido-disponible", "contador-ingerido-disponible");
    actualizarContador("tabla-ingerido-asignado", "contador-ingerido-asignado");

    actualizarInputIngerido();
}

function actualizarInputIngerido() {
    const filas = document.querySelectorAll("#tabla-ingerido-asignado tbody tr");
    const ingeridos = [];

    filas.forEach(fila => {
        const clave = fila.cells[0].textContent.trim();
        const descripcion = fila.cells[1].textContent.trim();
        const unidad = fila.cells[2].textContent.trim();
        const cantidad = fila.cells[3].querySelector("input")?.value || "0";
        ingeridos.push({ clave, descripcion, unidad, cantidad });
    });

    document.getElementById("input-ingerido").value = JSON.stringify(ingeridos);
}

function eliminarSeleccionadosIngerido() {
    const asignados = document.querySelectorAll("#tabla-ingerido-asignado tbody tr");
    const disponibles = document.querySelector("#tabla-ingerido-disponible tbody");

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

    actualizarContador("tabla-ingerido-disponible", "contador-ingerido-disponible");
}

function actualizarContador(idTabla, idContador) {
    const tabla = document.querySelector(`#${idTabla} tbody`);
    const contador = document.getElementById(idContador);
    contador.textContent = `[ ${tabla.children.length} ]`;
}

document.addEventListener("DOMContentLoaded", function () {
    actualizarInputIngerido();
    eliminarSeleccionadosIngerido();
    actualizarContador("tabla-ingerido-disponible", "contador-ingerido-disponible");
    actualizarContador("tabla-ingerido-asignado", "contador-ingerido-asignado");

    const filasAsignadasInge = document.querySelectorAll("#tabla-ingerido-asignado tbody tr");
    filasAsignadasInge.forEach(fila => {
        const clave = fila.cells[0]?.textContent.trim();
        const nombre = fila.cells[1]?.textContent.trim();
        const unidad = fila.cells[2]?.textContent.trim();
        fila.ondblclick = function () {
            moverADisponiblesIngerido(this, clave, nombre, unidad);
        };
    });
});
