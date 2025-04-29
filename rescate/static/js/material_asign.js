let materialesDisponibles = document.querySelector("#tabla-materiales-disponibles tbody");
let materialesAsignados = document.querySelector("#tabla-materiales-asignados tbody");
let inputMateriales = document.querySelector("#input-materiales-seleccionados");

function moverASeleccionadosMaterial(row, clave, descripcion, unidad) {
    row.remove();

    let nuevaFila = document.createElement("tr");
    nuevaFila.innerHTML = `
        <td>${descripcion}</td>
        <td>${unidad}</td>
        <td><input type="number" value="1" class="form-control cantidad-material" /></td>
    `;

    const cantidadInput = nuevaFila.querySelector(".cantidad-material");
    cantidadInput.addEventListener("input", function() {
        inputCantidadMaterial.value = cantidadInput.value;
    });

    const inputClaveMaterial = document.createElement("input");
    inputClaveMaterial.type = "hidden";
    inputClaveMaterial.name = `materiales[${clave}][clave]`;
    inputClaveMaterial.value = clave;
    document.forms[0].appendChild(inputClaveMaterial);

    const inputDescripcionMaterial = document.createElement("input");
    inputDescripcionMaterial.type = "hidden";
    inputDescripcionMaterial.name = `materiales[${clave}][descripcion]`;
    inputDescripcionMaterial.value = descripcion; 
    document.forms[0].appendChild(inputDescripcionMaterial);

    const inputCantidadMaterial = document.createElement("input");
    inputCantidadMaterial.type = "hidden";
    inputCantidadMaterial.name = `materiales[${clave}][cantidad]`;
    inputCantidadMaterial.value = cantidadInput.value;; 
    document.forms[0].appendChild(inputCantidadMaterial);

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
        let clave = row.children[0].textContent.trim();
        let unidad = row.children[1].textContent.trim();
        let cantidad = row.children[2].querySelector("input").value;
        return { clave, unidad, cantidad };
    });

    inputMateriales.value = JSON.stringify(datos);
}

function actualizarContadores() {
    document.getElementById("contador-materiales-disponibles").textContent = "[ " + materialesDisponibles.children.length + " ]";
    document.getElementById("contador-materiales-asignados").textContent = "[ " + materialesAsignados.children.length + " ]";
}

document.addEventListener("DOMContentLoaded", actualizarContadores);
