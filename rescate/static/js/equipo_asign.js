let equipoDisponibles = document.querySelector("#tabla-equipo-disponible tbody");
let equipoAsignados = document.querySelector("#tabla-equipo-asignado tbody");
let inputEquipo = document.querySelector("#input-equipo-seleccionado");

function moverASeleccionadosequipo(row, clave, descripcion, unidad) {
    row.remove();

    let nuevaFila = document.createElement("tr");
    nuevaFila.innerHTML = `
        <td>${descripcion}</td>
        <td>${unidad}</td>
        <td>
            <input type="number" class="form-control form-control-sm" value="1" min="1">
        </td>
    `;
    nuevaFila.ondblclick = function () {
        moverADisponiblesequipo(nuevaFila, clave, descripcion, unidad);
    };

    equipoAsignados.appendChild(nuevaFila);
    actualizarContadoresequipo();
}

function moverADisponiblesequipo(row, clave, descripcion, unidad) {
    row.remove();

    let nuevaFila = document.createElement("tr");
    nuevaFila.innerHTML = `
        <td>${clave}</td>
        <td>${descripcion}</td>
        <td style="display: none;">${unidad || ''}</td>
    `;
    nuevaFila.ondblclick = function () {
        moverASeleccionadosequipo(nuevaFila, clave, descripcion, unidad);
    };

    equipoDisponibles.appendChild(nuevaFila);
    actualizarContadoresequipo();
}

function actualizarContadoresequipo() {
    document.getElementById("contador-equipo-disponible").textContent = "[ " + equipoDisponibles.children.length + " ]";
    document.getElementById("contador-equipo-asignado").textContent = "[ " + equipoAsignados.children.length + " ]";
}

document.addEventListener("DOMContentLoaded", () => {
    Array.from(equipoDisponibles.querySelectorAll("tr")).forEach(row => {
        const clave = row.children[0].textContent.trim();
        const descripcion = row.children[1].textContent.trim();
        const unidad = row.children[2]?.textContent.trim() || '';
        row.ondblclick = function () {
            moverASeleccionadosequipo(row, clave, descripcion, unidad);
        };
    });

    actualizarContadoresequipo();
});