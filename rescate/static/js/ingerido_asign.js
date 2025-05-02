let ingeridoDisponibles = document.querySelector("#tabla-ingerido-disponible tbody");
let ingeridoAsignados = document.querySelector("#tabla-ingerido-asignado tbody");
let inputIngerido = document.querySelector("#input-ingerido-seleccionados");

function moverASeleccionadosIngerido(row, clave, descripcion, unidad) {
    row.remove();

    let nuevaFila = document.createElement("tr");
    nuevaFila.innerHTML = `
        <td>${descripcion}</td>
        <td>${unidad}</td>
        <td><input type="number" value="1" class="form-control cantidad-ingerido" min="1" /></td>
    `;

    const cantidadInput = nuevaFila.querySelector(".cantidad-ingerido");

    const inputClave = document.createElement("input");
    inputClave.type = "hidden";
    inputClave.name = `ingeridos[${clave}][clave]`;
    inputClave.value = clave;
    document.forms[0].appendChild(inputClave);

    const inputDescripcion = document.createElement("input");
    inputDescripcion.type = "hidden";
    inputDescripcion.name = `ingeridos[${clave}][descripcion]`;
    inputDescripcion.value = descripcion;
    document.forms[0].appendChild(inputDescripcion);

    const inputCantidad = document.createElement("input");
    inputCantidad.type = "hidden";
    inputCantidad.name = `ingeridos[${clave}][cantidad]`;
    inputCantidad.value = cantidadInput.value;
    document.forms[0].appendChild(inputCantidad);

    cantidadInput.addEventListener("input", function () {
        inputCantidad.value = cantidadInput.value;
        actualizarInputIngerido();
    });

    nuevaFila.ondblclick = function () {
        moverADisponiblesIngerido(nuevaFila, clave, descripcion, unidad);
    };

    ingeridoAsignados.appendChild(nuevaFila);
    actualizarInputIngerido();
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
    actualizarInputIngerido();
    actualizarContadoresIngerido();
}

function actualizarInputIngerido() {
    let datos = Array.from(ingeridoAsignados.querySelectorAll("tr")).map(row => {
        let descripcion = row.children[0].textContent.trim();
        let unidad = row.children[1].textContent.trim();
        let cantidad = row.children[2].querySelector("input").value;
        return { descripcion, unidad, cantidad };
    });

    inputIngerido.value = JSON.stringify(datos);
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
