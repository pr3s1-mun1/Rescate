let administradoDisponibles = document.querySelector("#tabla-administrado-disponible tbody");
let administradoAsignados = document.querySelector("#tabla-administrado-asignado tbody");
let inputadministrado = document.querySelector("#input-administrado-seleccionados");

function moverASeleccionadosadministrado(row, clave, descripcion, unidad) {
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
        moverADisponiblesadministrado(nuevaFila, clave, descripcion, unidad);
    };

    administradoAsignados.appendChild(nuevaFila);
    actualizarContadoresadministrado();
}

function moverADisponiblesadministrado(row, clave, descripcion, unidad) {
    row.remove();

    let nuevaFila = document.createElement("tr");
    nuevaFila.innerHTML = `
        <td>${clave}</td>
        <td>${descripcion}</td>
        <td style="display: none;">${unidad || ''}</td>
    `;
    nuevaFila.ondblclick = function () {
        moverASeleccionadosadministrado(nuevaFila, clave, descripcion, unidad);
    };

    administradoDisponibles.appendChild(nuevaFila);
    actualizarContadoresadministrado();
}

function actualizarContadoresadministrado() {
    document.getElementById("contador-administrado-disponible").textContent = "[ " + administradoDisponibles.children.length + " ]";
    document.getElementById("contador-administrado-asignado").textContent = "[ " + administradoAsignados.children.length + " ]";
}

document.addEventListener("DOMContentLoaded", () => {
    Array.from(administradoDisponibles.querySelectorAll("tr")).forEach(row => {
        const clave = row.children[0].textContent.trim();
        const descripcion = row.children[1].textContent.trim();
        const unidad = row.children[2]?.textContent.trim() || '';
        row.ondblclick = function () {
            moverASeleccionadosadministrado(row, clave, descripcion, unidad);
        };
    });

    actualizarContadoresadministrado();
});