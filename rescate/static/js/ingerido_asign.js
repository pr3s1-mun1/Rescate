let ingeridoDisponibles = document.querySelector("#tabla-ingerido-disponible tbody");
let ingeridoAsignados = document.querySelector("#tabla-ingerido-asignado tbody");
let inputIngerido = document.querySelector("#input-ingerido-seleccionados");

function moverASeleccionadosIngerido(row, clave, descripcion, unidad) {
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
        moverADisponiblesIngerido(nuevaFila, clave, descripcion, unidad);
    };

    ingeridoAsignados.appendChild(nuevaFila);
    actualizarContadoresIngerido();
}

function moverADisponiblesIngerido(row, clave, descripcion, unidad) {
    row.remove();

    let nuevaFila = document.createElement("tr");
    nuevaFila.innerHTML = `
        <td>${clave}</td>
        <td>${descripcion}</td>
        <td style="display: none;">${unidad}</td>
    `;
    nuevaFila.ondblclick = function () {
        moverASeleccionadosIngerido(nuevaFila, clave, descripcion, unidad);
    };

    ingeridoDisponibles.appendChild(nuevaFila);
    actualizarContadoresIngerido();
}

function actualizarContadoresIngerido() {
    document.getElementById("contador-ingerido-disponible").textContent = "[ " + ingeridoDisponibles.children.length + " ]";
    document.getElementById("contador-ingerido-asignado").textContent = "[ " + ingeridoAsignados.children.length + " ]";
}

document.addEventListener("DOMContentLoaded", () => {
    Array.from(ingeridoDisponibles.querySelectorAll("tr")).forEach(row => {
        const clave = row.children[0].textContent.trim();
        const descripcion = row.children[1].textContent.trim();
        const unidad = row.children[2]?.textContent.trim() || ''; 
        row.ondblclick = function () {
            moverASeleccionadosIngerido(row, clave, descripcion, unidad);
        };
    });

    actualizarContadoresIngerido();
});