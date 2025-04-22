let materialesDisponibles = document.querySelector("#tabla-materiales-disponibles tbody");
let materialesAsignados = document.querySelector("#tabla-materiales-asignados tbody");
let inputMateriales = document.querySelector("#input-materiales-seleccionados");

function moverASeleccionadosMaterial(row, clave, descripcion, unidad) {
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
        moverADisponiblesMaterial(nuevaFila, clave, descripcion, unidad);
    };

    materialesAsignados.appendChild(nuevaFila);
    actualizarInputMateriales();
    actualizarContadores();
}

function moverADisponiblesMaterial(row, clave, descripcion, unidad) {
    row.remove();

    let nuevaFila = document.createElement("tr");
    nuevaFila.innerHTML = `
        <td>${clave}</td>
        <td>${descripcion}</td>
    `;
    nuevaFila.ondblclick = function () {
        moverASeleccionadosMaterial(nuevaFila, clave, descripcion, unidad);
    };

    materialesDisponibles.appendChild(nuevaFila);
    actualizarInputMateriales();
    actualizarContadores();
}

function actualizarInputMateriales() {
    let datos = Array.from(materialesAsignados.querySelectorAll("tr")).map(row => {
        let descripcion = row.children[0].textContent.trim();
        let unidad = row.children[1].textContent.trim();
        let cantidad = row.children[2].querySelector("input").value;
        return { descripcion, unidad, cantidad };
    });

    inputMateriales.value = JSON.stringify(datos);
}

function actualizarContadores() {
    document.getElementById("contador-materiales-disponibles").textContent = "[ " + materialesDisponibles.children.length + " ]";
    document.getElementById("contador-materiales-asignados").textContent = "[ " + materialesAsignados.children.length + " ]";
}

document.addEventListener("DOMContentLoaded", actualizarContadores);
