function moverASeleccionadosAlergia(fila, clave, nombre) {
    const yaSeleccionado = document.querySelector(`#tabla-alergias-asignadas tbody tr[data-nombre="${nombre}"]`);
    if (yaSeleccionado) return;

    const tablaAsignados = document.querySelector("#tabla-alergias-asignadas tbody");
    const nuevaFila = tablaAsignados.insertRow();
    nuevaFila.setAttribute("data-nombre", nombre);

    nuevaFila.ondblclick = function () {
        moverAOriginalesAlergia(this, clave, nombre);
    };

    const celdaClave = nuevaFila.insertCell(0);
    celdaClave.textContent = clave;

    const celdaNombre = nuevaFila.insertCell(1);
    celdaNombre.textContent = nombre;

    const inputClaveAlergia = document.createElement("input");
    inputClaveAlergia.type = "hidden";
    inputClaveAlergia.name = `alergias[${clave}][clave]`;
    inputClaveAlergia.value = clave;
    document.forms[0].appendChild(inputClaveAlergia);

    const inputNombreAlergia = document.createElement("input");
    inputNombreAlergia.type = "hidden";
    inputNombreAlergia.name = `alergias[${clave}][descripcion]`;
    inputNombreAlergia.value = nombre;
    document.forms[0].appendChild(inputNombreAlergia);

    fila.remove();

    actualizarContadorAlergia("tabla-alergias-disponibles", "contador-alergias-disponibles");
    actualizarContadorAlergia("tabla-alergias-asignadas", "contador-alergias-asignadas");
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

    actualizarContadorAlergia("tabla-alergias-disponibles", "contador-alergias-disponibles");
    actualizarContadorAlergia("tabla-alergias-asignadas", "contador-alergias-asignadas");
}

function actualizarContadorAlergia(idTabla, idContador) {
    const totalFilas = document.querySelectorAll(`#${idTabla} tbody tr:not(.d-none)`).length;
    document.getElementById(idContador).textContent = totalFilas;
}

document.addEventListener("DOMContentLoaded", function () {
    const filasDisponibles = document.querySelectorAll("#tabla-alergias-disponibles tbody tr");
    filasDisponibles.forEach(fila => {
        fila.addEventListener("dblclick", function () {
            const clave = this.cells[0].textContent.trim();
            const nombre = this.cells[1].textContent.trim();
            moverASeleccionadosAlergia(this, clave, nombre);
        });
    });

    const filasAsignados = document.querySelectorAll("#tabla-alergias-asignadas tbody tr");
    filasAsignados.forEach(fila => {
        fila.addEventListener("dblclick", function () {
            const clave = this.cells[0].textContent.trim();
            const nombre = this.cells[1].textContent.trim();
            moverAOriginalesAlergia(this, clave, nombre);
        });
    });

    actualizarContadorAlergia("tabla-alergias-disponibles", "contador-alergias-disponibles");
    actualizarContadorAlergia("tabla-alergias-asignadas", "contador-alergias-asignadas");
});
