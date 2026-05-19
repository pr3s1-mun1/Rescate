function moverASeleccionadosProcedimiento(fila, clave, nombre, protocolo) {
    const yaSeleccionado = document.querySelector(`#tabla-procedimientos-asignados tbody tr[data-nombre="${nombre}"]`);
    if (yaSeleccionado) return;

    const tablaAsignados = document.querySelector("#tabla-procedimientos-asignados tbody");
    const nuevaFila = tablaAsignados.insertRow();
    nuevaFila.setAttribute("data-nombre", nombre);

    nuevaFila.ondblclick = function () {
        moverAOriginalesProcedimiento(this, clave, nombre, protocolo);
    };

    nuevaFila.insertCell(0).textContent = clave;
    nuevaFila.insertCell(1).textContent = nombre;
    nuevaFila.insertCell(2).textContent = protocolo;

    fila.remove();

    actualizarContador("tabla-procedimientos-disponibles", "contador-procedimientos-disponibles");
    actualizarContador("tabla-procedimientos-asignados", "contador-procedimientos-asignados");

    actualizarInputProcedmientos();
}

function moverAOriginalesProcedimiento(fila, clave, nombre, protocolo) {
    const tablaDisponibles = document.querySelector("#tabla-procedimientos-disponibles tbody");
    const nuevaFila = tablaDisponibles.insertRow();
    nuevaFila.setAttribute("data-clave", clave);

    nuevaFila.ondblclick = function () {
        moverASeleccionadosProcedimiento(this, clave, nombre, protocolo);
    };

    nuevaFila.insertCell(0).textContent = clave;
    nuevaFila.insertCell(1).textContent = nombre;
    nuevaFila.insertCell(2).textContent = protocolo;

    fila.remove();

    actualizarContador("tabla-procedimientos-disponibles", "contador-procedimientos-disponibles");
    actualizarContador("tabla-procedimientos-asignados", "contador-procedimientos-asignados");

    actualizarInputProcedmientos();
}

function actualizarInputProcedmientos() {
    const filas = document.querySelectorAll("#tabla-procedimientos-asignados tbody tr");
    const procedimientos = [];

    filas.forEach(fila => {
        const clave = fila.cells[0].textContent.trim();
        const nombre = fila.cells[1].textContent.trim();
        const protocolo = fila.cells[2].textContent.trim();
        procedimientos.push({ clave, nombre, protocolo });
    });

    // Aquí se debe usar 'procedimientos' en lugar de 'paramedicos'
    document.getElementById("input-procedimientos").value = JSON.stringify(procedimientos);
}

function eliminarSeleccionados() {
    const asignados = document.querySelectorAll("#tabla-procedimientos-asignados tbody tr");
    const disponibles = document.querySelector("#tabla-procedimientos-disponibles tbody");

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

    actualizarContador("tabla-procedimientos-disponibles", "contador-procedimientos-disponibles");
}

document.addEventListener("DOMContentLoaded", function () {
    actualizarInputProcedmientos();
    eliminarSeleccionados();
    actualizarContador("tabla-procedimientos-disponibles", "contador-procedimientos-disponibles");
    actualizarContador("tabla-procedimientos-asignados", "contador-procedimientos-asignados");
    const filasAsignadas = document.querySelectorAll("#tabla-procedimientos-asignados tbody tr");
    filasAsignadas.forEach(fila => {
        const clave = fila.cells[0]?.textContent.trim();
        const nombre = fila.cells[1]?.textContent.trim();
        const protocolo = fila.cells[2]?.textContent.trim();

        fila.ondblclick = function () {
            moverAOriginalesProcedimiento(this, clave, nombre, protocolo);
        };
    });
});
