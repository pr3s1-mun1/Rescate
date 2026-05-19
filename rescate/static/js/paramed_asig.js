function moverASeleccionados(fila, clave, nombre) {
    const yaSeleccionado = document.querySelector(`#tabla-paramedicos-asignados tbody tr[data-clave="${clave}"]`);
    if (yaSeleccionado) return;

    const tablaAsignados = document.querySelector("#tabla-paramedicos-asignados tbody");
    const nuevaFila = tablaAsignados.insertRow();
    nuevaFila.setAttribute("data-clave", clave);

    nuevaFila.ondblclick = function () {
        moverAOriginales(this, clave, nombre);
    };

    nuevaFila.insertCell(0).textContent = clave;
    nuevaFila.insertCell(1).textContent = nombre;

    fila.remove();

    actualizarContador("tabla-paramedicos-disponibles", "contador-paramedicos-disponibles");
    actualizarContador("tabla-paramedicos-asignados", "contador-paramedicos-asignados");

    actualizarInputParamedicos();
}

function moverAOriginales(fila, clave, nombre) {
    const yaDisponible = document.querySelector(`#tabla-paramedicos-disponibles tbody tr[data-clave="${clave}"]`);
    if (yaDisponible) return;

    const tablaDisponibles = document.querySelector("#tabla-paramedicos-disponibles tbody");
    const nuevaFila = tablaDisponibles.insertRow();
    nuevaFila.setAttribute("data-clave", clave);

    nuevaFila.ondblclick = function () {
        moverASeleccionados(this, clave, nombre);
    };

    nuevaFila.insertCell(0).textContent = clave;
    nuevaFila.insertCell(1).textContent = nombre;

    fila.remove();

    actualizarContador("tabla-paramedicos-disponibles", "contador-paramedicos-disponibles");
    actualizarContador("tabla-paramedicos-asignados", "contador-paramedicos-asignados");

    actualizarInputParamedicos();
}

function actualizarInputParamedicos() {
    const filas = document.querySelectorAll("#tabla-paramedicos-asignados tbody tr");
    const paramedicos = [];

    filas.forEach(fila => {
        const clave = fila.cells[0].textContent.trim();
        const nombre = fila.cells[1].textContent.trim();
        paramedicos.push({ clave, nombre });
    });

    document.getElementById("input-paramedicos").value = JSON.stringify(paramedicos);
}

function eliminarSeleccionadosParamedicos() {
    const asignados = document.querySelectorAll("#tabla-paramedicos-asignados tbody tr");
    const disponibles = document.querySelector("#tabla-paramedicos-disponibles tbody");

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

document.addEventListener("DOMContentLoaded", function () {
    actualizarInputParamedicos();
    eliminarSeleccionadosParamedicos();
    actualizarContador("tabla-paramedicos-disponibles", "contador-paramedicos-disponibles");
    actualizarContador("tabla-paramedicos-asignados", "contador-paramedicos-asignados");

    const filasAsignadasParamedicos = document.querySelectorAll("#tabla-paramedicos-asignados tbody tr");
    filasAsignadasParamedicos.forEach(fila => {
        const clave = fila.cells[0]?.textContent.trim();
        const nombre = fila.cells[1]?.textContent.trim();

        fila.ondblclick = function () {
            moverAOriginales(this, clave, nombre);
        };
    });

});
