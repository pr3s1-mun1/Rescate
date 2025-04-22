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

    fila.remove();

    actualizarContador("tabla-alergias-disponibles", "contador-alergias-disponibles");
    actualizarContador("tabla-alergias-asignadas", "contador-alergias-asignadas");
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

    const filasAsignadas = document.querySelectorAll("#tabla-alergias-asignadas tbody tr");
    filasAsignadas.forEach(fila => {
        fila.addEventListener("dblclick", function () {
            const clave = this.cells[0].textContent.trim();
            const nombre = this.cells[1].textContent.trim();
            moverAOriginalesAlergia(this, clave, nombre);
        });
    });

    actualizarContador("tabla-alergias-disponibles", "contador-alergias-disponibles");
    actualizarContador("tabla-alergias-asignadas", "contador-alergias-asignadas");

    const form = document.querySelector("form");
    if (form) {
        form.addEventListener("submit", function (e) {
            const seleccionados = [];
            document.querySelectorAll("#tabla-alergias-asignadas tbody tr").forEach(tr => {
                const clave = tr.cells[0].textContent.trim();
                const nombre = tr.cells[1].textContent.trim();
                seleccionados.push({ clave, nombre });
            });

            const inputOculto = document.getElementById("input-alergias-seleccionadas");
            if (inputOculto) {
                inputOculto.value = JSON.stringify(seleccionados);
            }
        });
    }
});
