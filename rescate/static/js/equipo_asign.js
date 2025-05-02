let equipoDisponibles = document.querySelector("#tabla-equipo-disponible tbody");
let equipoAsignados = document.querySelector("#tabla-equipo-asignado tbody");
let inputEquipo = document.querySelector("#input-equipo-seleccionado");

function moverASeleccionadosequipo(row, clave, descripcion, unidad) {
    row.remove();

    let nuevaFila = document.createElement("tr");
    nuevaFila.dataset.clave = clave;  // Se guarda la clave en un atributo del <tr>
    nuevaFila.innerHTML = `
        <td>${descripcion}</td>
        <td>${unidad}</td>
        <td>
            <input type="number" class="form-control form-control-sm" value="1" min="1">
        </td>
    `;

    const cantidadInput = nuevaFila.querySelector("input");

    // Inputs ocultos para enviar al backend
    const inputClave = document.createElement("input");
    inputClave.type = "hidden";
    inputClave.name = `equipos[${clave}][clave]`;
    inputClave.value = clave;
    inputClave.classList.add(`equipo-hidden-${clave}`);
    document.forms[0].appendChild(inputClave);

    const inputDescripcion = document.createElement("input");
    inputDescripcion.type = "hidden";
    inputDescripcion.name = `equipos[${clave}][descripcion]`;
    inputDescripcion.value = descripcion;
    inputDescripcion.classList.add(`equipo-hidden-${clave}`);
    document.forms[0].appendChild(inputDescripcion);

    const inputCantidad = document.createElement("input");
    inputCantidad.type = "hidden";
    inputCantidad.name = `equipos[${clave}][cantidad]`;
    inputCantidad.value = cantidadInput.value;
    inputCantidad.classList.add(`equipo-hidden-${clave}`);
    document.forms[0].appendChild(inputCantidad);

    cantidadInput.addEventListener("input", function () {
        inputCantidad.value = cantidadInput.value;
        actualizarInputEquipo();
    });

    nuevaFila.ondblclick = function () {
        moverADisponiblesequipo(nuevaFila, clave, descripcion, unidad);
    };

    equipoAsignados.appendChild(nuevaFila);
    actualizarInputEquipo();
    actualizarContadoresequipo();
}

function moverADisponiblesequipo(row, clave, descripcion, unidad) {
    row.remove();

    // Eliminar inputs ocultos del formulario
    document.querySelectorAll(`.equipo-hidden-${clave}`).forEach(input => input.remove());

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
    actualizarInputEquipo();
    actualizarContadoresequipo();
}

function actualizarInputEquipo() {
    let datos = Array.from(equipoAsignados.querySelectorAll("tr")).map(row => {
        let clave = row.dataset.clave;
        let descripcion = row.children[0].textContent.trim();
        let unidad = row.children[1].textContent.trim();
        let cantidad = row.children[2].querySelector("input").value;
        return { clave, descripcion, unidad, cantidad };
    });

    inputEquipo.value = JSON.stringify(datos);
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
