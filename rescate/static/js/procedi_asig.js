function moverASeleccionadosProcedimiento(fila, clave, nombre) {
    const yaSeleccionado = document.querySelector(`#tabla-procedimientos-asignados tbody tr[data-nombre="${nombre}"]`);
    if (yaSeleccionado) return;

    const tablaAsignados = document.querySelector("#tabla-procedimientos-asignados tbody");
    const nuevaFila = tablaAsignados.insertRow();
    nuevaFila.setAttribute("data-nombre", nombre);

    nuevaFila.ondblclick = function () {
        moverAOriginalesProcedimiento(this, clave, nombre);
    };

    const celdaClave = nuevaFila.insertCell(0);
    celdaClave.textContent = clave;

    const celdaNombre = nuevaFila.insertCell(1);
    celdaNombre.textContent = nombre;

    fila.remove();

    actualizarContador("tabla-procedimientos-disponibles", "contador-procedimientos-disponibles");
    actualizarContador("tabla-procedimientos-asignados", "contador-procedimientos-asignados");
}

function moverAOriginalesProcedimiento(fila, clave, nombre) {
    const tablaDisponibles = document.querySelector("#tabla-procedimientos-disponibles tbody");
    const nuevaFila = tablaDisponibles.insertRow();
    nuevaFila.setAttribute("data-clave", clave);

    nuevaFila.ondblclick = function () {
        moverASeleccionadosProcedimiento(this, clave, nombre);
    };

    const celdaClave = nuevaFila.insertCell(0);
    celdaClave.textContent = clave;

    const celdaNombre = nuevaFila.insertCell(1);
    celdaNombre.textContent = nombre;

    fila.remove();

    actualizarContador("tabla-procedimientos-disponibles", "contador-procedimientos-disponibles");
    actualizarContador("tabla-procedimientos-asignados", "contador-procedimientos-asignados");
}

function actualizarContadorProcedimiento(idTabla, idContador) {
    const totalFilas = document.querySelectorAll(`#${idTabla} tbody tr:not(.d-none)`).length;
    document.getElementById(idContador).textContent = totalFilas;
}

document.addEventListener("DOMContentLoaded", function () {
    const filasDisponibles = document.querySelectorAll("#tabla-procedimientos-disponibles tbody tr");
    filasDisponibles.forEach(fila => {
        fila.addEventListener("dblclick", function () {
            const clave = this.cells[0].textContent.trim();
            const nombre = this.cells[1].textContent.trim();
            moverASeleccionadosProcedimiento(this, clave, nombre);
        });
    });
    
    const filasAsignados = document.querySelectorAll("#tabla-procedimientos-asignados tbody tr");
    filasAsignados.forEach(fila => {
        fila.addEventListener("dblclick", function () {
            const clave = this.cells[0].textContent.trim();
            const nombre = this.cells[1].textContent.trim();
            moverAOriginalesProcedimiento(this, clave, nombre);
        });
    });

    actualizarContador("tabla-procedimientos-disponibles", "contador-procedimientos-disponibles");
    actualizarContador("tabla-procedimientos-asignados", "contador-procedimientos-asignados");

    const form = document.querySelector("form");
    if (form) {
        form.addEventListener("submit", function (e) {
            const seleccionados = [];
            document.querySelectorAll("#tabla-procedimientos-asignados tbody tr").forEach(tr => {
                const clave = tr.cells[0].textContent.trim();
                const nombre = tr.cells[1].textContent.trim();
                seleccionados.push({ clave, nombre });
            });

            const inputOculto = document.getElementById("input-procedimientos-seleccionados");
            if (inputOculto) {
                inputOculto.value = JSON.stringify(seleccionados);
            }
        });
    }
});

