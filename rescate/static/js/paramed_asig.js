function moverASeleccionados(fila, clave, nombre) {
    // Verificar si la fila ya está en la tabla de asignados
    const yaSeleccionado = document.querySelector(`#tabla-paramedicos-asignados tbody tr[data-clave="${clave}"]`);
    if (yaSeleccionado) return; // Evitar que se mueva si ya está asignado

    const tablaAsignados = document.querySelector("#tabla-paramedicos-asignados tbody");
    const nuevaFila = tablaAsignados.insertRow();
    nuevaFila.setAttribute("data-clave", clave);

    // Verificar si el evento ya existe antes de asignarlo
    if (!nuevaFila.ondblclick) {
        nuevaFila.ondblclick = function () {
            moverAOriginales(this, clave, nombre);
        };
    }

    const celdaClave = nuevaFila.insertCell(0);
    celdaClave.textContent = clave;

    const celdaNombre = nuevaFila.insertCell(1);
    celdaNombre.textContent = nombre;

    const total = document.querySelectorAll('input[name^="paramedicos["]').length;
    console.log("Número de listas: " + total);
    
    const inputParamedico = document.createElement("input");
    inputParamedico.type = "hidden";
    inputParamedico.name = `paramedicos[${total}][clave]`;
    inputParamedico.value = clave;
    inputParamedico.setAttribute("data-clave", clave); // Para poder eliminarlo después
    document.forms[0].appendChild(inputParamedico);

    fila.remove(); // Eliminar de la tabla original

    actualizarContador("tabla-paramedicos-disponibles", "contador-paramedicos-disponibles");
    actualizarContador("tabla-paramedicos-asignados", "contador-paramedicos-asignados");
}


function moverAOriginales(fila, clave, nombre) {
    // Verificar si la fila ya está en la tabla de disponibles
    const yaDisponible = document.querySelector(`#tabla-paramedicos-disponibles tbody tr[data-clave="${clave}"]`);
    if (yaDisponible) return; // Evitar que se mueva si ya está disponible

    const tablaDisponibles = document.querySelector("#tabla-paramedicos-disponibles tbody");
    const nuevaFila = tablaDisponibles.insertRow();
    nuevaFila.setAttribute("data-clave", clave);

    // Verificar si el evento ya existe antes de asignarlo
    if (!nuevaFila.ondblclick) {
        nuevaFila.ondblclick = function () {
            moverASeleccionados(this, clave, nombre);
        };
    }

    const celdaClave = nuevaFila.insertCell(0);
    celdaClave.textContent = clave;

    const celdaNombre = nuevaFila.insertCell(1);
    celdaNombre.textContent = nombre;

    const inputParamedico = document.querySelector(`input[type="hidden"][data-clave="${clave}"]`);
    if (inputParamedico) {
        inputParamedico.remove();
    }

    fila.remove(); // Eliminar de la tabla asignada

    actualizarContador("tabla-paramedicos-disponibles", "contador-paramedicos-disponibles");
    actualizarContador("tabla-paramedicos-asignados", "contador-paramedicos-asignados");
}


document.addEventListener("DOMContentLoaded", function () {
    actualizarContador("tabla-paramedicos-disponibles", "contador-paramedicos-disponibles");
    actualizarContador("tabla-paramedicos-asignados", "contador-paramedicos-asignados");
});
