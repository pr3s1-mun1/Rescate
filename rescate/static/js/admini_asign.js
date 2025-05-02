let administradoDisponibles = document.querySelector("#tabla-administrado-disponible tbody");
let administradoAsignados = document.querySelector("#tabla-administrado-asignado tbody");
let inputadministrado = document.querySelector("#input-administrado-seleccionado");

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

    const cantidadInput = nuevaFila.querySelector("input");

    const inputClave = document.createElement("input");
    inputClave.type = "hidden";
    inputClave.name = `administrados[${clave}][clave]`;
    inputClave.value = clave;
    inputClave.classList.add(`administrado-hidden-${clave}`);
    document.forms[0].appendChild(inputClave);

    const inputDescripcion = document.createElement("input");
    inputDescripcion.type = "hidden";
    inputDescripcion.name = `administrados[${clave}][descripcion]`;
    inputDescripcion.value = descripcion;
    inputDescripcion.classList.add(`administrado-hidden-${clave}`);
    document.forms[0].appendChild(inputDescripcion);

    const inputCantidad = document.createElement("input");
    inputCantidad.type = "hidden";
    inputCantidad.name = `administrados[${clave}][cantidad]`;
    inputCantidad.value = cantidadInput.value;
    inputCantidad.classList.add(`administrado-hidden-${clave}`);
    document.forms[0].appendChild(inputCantidad);

    cantidadInput.addEventListener("input", function () {
        inputCantidad.value = cantidadInput.value;
        actualizarInputAdministrado();
    });

    nuevaFila.ondblclick = function () {
        moverADisponiblesadministrado(nuevaFila, clave, descripcion, unidad);
    };

    administradoAsignados.appendChild(nuevaFila);
    actualizarInputAdministrado();
    actualizarContadoresadministrado();
}

function moverADisponiblesadministrado(row, clave, descripcion, unidad) {
    row.remove();

    // Eliminar inputs ocultos
    document.querySelectorAll(`.administrado-hidden-${clave}`).forEach(input => input.remove());

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
    actualizarInputAdministrado();
    actualizarContadoresadministrado();
}

function actualizarInputAdministrado() {
    let datos = Array.from(administradoAsignados.querySelectorAll("tr")).map(row => {
        let descripcion = row.children[0].textContent.trim();
        let unidad = row.children[1].textContent.trim();
        let cantidad = row.children[2].querySelector("input").value;
        return { descripcion, unidad, cantidad };
    });

    inputadministrado.value = JSON.stringify(datos);
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
