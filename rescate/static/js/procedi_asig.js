function moverASeleccionadosProcedimiento(fila, clave, nombre, protocolo) {
    const yaSeleccionado = document.querySelector(`#tabla-procedimientos-asignados tbody tr[data-nombre="${nombre}"]`);
    if (yaSeleccionado) return;

    const tablaAsignados = document.querySelector("#tabla-procedimientos-asignados tbody");
    const nuevaFila = tablaAsignados.insertRow();
    nuevaFila.setAttribute("data-nombre", nombre);

    nuevaFila.ondblclick = function () {
        moverAOriginalesProcedimiento(this, clave, nombre, protocolo);
    };

    const celdaClave = nuevaFila.insertCell(0);
    celdaClave.textContent = clave;

    const celdaNombre = nuevaFila.insertCell(1);
    celdaNombre.textContent = nombre;

    const celdaProtocolo = nuevaFila.insertCell(2);
    celdaProtocolo.textContent = protocolo; 

    const inputClaveProcedimiento = document.createElement("input");
    inputClaveProcedimiento.type = "hidden";
    inputClaveProcedimiento.name = `procedimientos[${clave}][clave]`;
    inputClaveProcedimiento.value = clave;
    document.forms[0].appendChild(inputClaveProcedimiento);

    const inputNombreProcedimiento = document.createElement("input");
    inputNombreProcedimiento.type = "hidden";
    inputNombreProcedimiento.name = `procedimientos[${clave}][descripcion]`;
    inputNombreProcedimiento.value = nombre;
    document.forms[0].appendChild(inputNombreProcedimiento);

    const inputProtocoloProcedimiento = document.createElement("input");
    inputProtocoloProcedimiento.type = "hidden";
    inputProtocoloProcedimiento.name = `procedimientos[${clave}][protocolo]`;
    inputProtocoloProcedimiento.value = protocolo;
    document.forms[0].appendChild(inputProtocoloProcedimiento);

    fila.remove();

    actualizarContadorProcedimiento("tabla-procedimientos-disponibles", "contador-procedimientos-disponibles");
    actualizarContadorProcedimiento("tabla-procedimientos-asignados", "contador-procedimientos-asignados");
}

function moverAOriginalesProcedimiento(fila, clave, nombre, protocolo) {
    const tablaDisponibles = document.querySelector("#tabla-procedimientos-disponibles tbody");
    const nuevaFila = tablaDisponibles.insertRow();
    nuevaFila.setAttribute("data-clave", clave);

    nuevaFila.ondblclick = function () {
        moverASeleccionadosProcedimiento(this, clave, nombre, protocolo);
    };

    const celdaClave = nuevaFila.insertCell(0);
    celdaClave.textContent = clave;

    const celdaNombre = nuevaFila.insertCell(1);
    celdaNombre.textContent = nombre;

    const celdaProtocolo = nuevaFila.insertCell(2);
    celdaProtocolo.textContent = protocolo;  

    fila.remove();

    actualizarContadorProcedimiento("tabla-procedimientos-disponibles", "contador-procedimientos-disponibles");
    actualizarContadorProcedimiento("tabla-procedimientos-asignados", "contador-procedimientos-asignados");
}

function actualizarContadorProcedimiento(idTabla, idContador) {
    const totalFilas = document.querySelectorAll(`#${idTabla} tbody tr:not(.d-none)`).length;
    document.getElementById(idContador).textContent = "[ " + totalFilas + " ]";
}

document.addEventListener("DOMContentLoaded", function () {
    const filasDisponibles = document.querySelectorAll("#tabla-procedimientos-disponibles tbody tr");
    filasDisponibles.forEach(fila => {
        fila.addEventListener("dblclick", function () {
            const clave = this.cells[0].textContent.trim();
            const nombre = this.cells[1].textContent.trim();
            const protocolo = this.cells[2].textContent.trim(); // Obtener el protocolo
            moverASeleccionadosProcedimiento(this, clave, nombre, protocolo);
        });
    });

    const filasAsignados = document.querySelectorAll("#tabla-procedimientos-asignados tbody tr");
    filasAsignados.forEach(fila => {
        fila.addEventListener("dblclick", function () {
            const clave = this.cells[0].textContent.trim();
            const nombre = this.cells[1].textContent.trim();
            const protocolo = this.cells[2].textContent.trim(); // Obtener el protocolo
            moverAOriginalesProcedimiento(this, clave, nombre, protocolo);
        });
    });

    actualizarContadorProcedimiento("tabla-procedimientos-disponibles", "contador-procedimientos-disponibles");
    actualizarContadorProcedimiento("tabla-procedimientos-asignados", "contador-procedimientos-asignados");
});
