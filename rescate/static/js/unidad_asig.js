function moverUnidadASeleccionados(fila, clave, descripcion) {
    const yaSeleccionado = document.querySelector(`#tabla-seleccionados tbody tr[data-clave="${clave}"]`);
    if (yaSeleccionado) return;

    let tablaSeleccionados = document.getElementById("tabla-seleccionados").getElementsByTagName('tbody')[0];

    let nuevaFila = tablaSeleccionados.insertRow();
    nuevaFila.setAttribute("data-clave", clave);

    let celdaTipo = nuevaFila.insertCell(0);
    celdaTipo.textContent = descripcion;

    let celdaIdUnidad = nuevaFila.insertCell(1);
    let inputIdUnidad = document.createElement("input");
    inputIdUnidad.type = "text";
    inputIdUnidad.className = "form-control";
    inputIdUnidad.name = `visible-unidades[${clave}][id_unidad]`;
    celdaIdUnidad.appendChild(inputIdUnidad);

    let celdaAgente = nuevaFila.insertCell(2);
    let inputAgente = document.createElement("input");
    inputAgente.type = "text";
    inputAgente.className = "form-control";
    inputAgente.name = `visible-unidades[${clave}][agente]`;
    celdaAgente.appendChild(inputAgente);

    // Crear input oculto para enviar la clave de la unidad seleccionada
    const inputClaveUnidad = document.createElement("input");
    inputClaveUnidad.type = "hidden";
    inputClaveUnidad.name = `unidades[${clave}][clave]`;
    inputClaveUnidad.value = clave;
    document.forms[0].appendChild(inputClaveUnidad);

    const inputIdUnidadOculto = document.createElement("input");
    inputIdUnidadOculto.type = "hidden";
    inputIdUnidadOculto.name = `unidades[${clave}][id_unidad]`;
    inputIdUnidadOculto.value = "";
    document.forms[0].appendChild(inputIdUnidadOculto);

    const inputAgenteOculto = document.createElement("input");
    inputAgenteOculto.type = "hidden";
    inputAgenteOculto.name = `unidades[${clave}][agente]`;
    inputAgenteOculto.value = "";
    document.forms[0].appendChild(inputAgenteOculto);

    inputIdUnidad.addEventListener("input", function() {
        inputIdUnidadOculto.value = inputIdUnidad.value;
    });

    inputAgente.addEventListener("input", function() {
        inputAgenteOculto.value = inputAgente.value;
    });

    nuevaFila.ondblclick = function () {
        tablaSeleccionados.deleteRow(nuevaFila.rowIndex - 1);
        // Eliminar el input oculto correspondiente a la unidad seleccionada
        const inputClaveUnidadEliminar = document.querySelector(`input[name="unidades[${clave}][clave]"]`);
        if (inputClaveUnidadEliminar) {
            inputClaveUnidadEliminar.remove();
        }
        const inputIdUnidadOcultoEliminar = document.querySelector(`input[name="unidades[${clave}][id_unidad]"]`);
        if (inputIdUnidadOcultoEliminar) {
            inputIdUnidadOcultoEliminar.remove();
        }
        const inputAgenteOcultoEliminar = document.querySelector(`input[name="unidades[${clave}][agente]"]`);
        if (inputAgenteOcultoEliminar) {
            inputAgenteOcultoEliminar.remove();
        }
        actualizarContador("tabla-seleccionados", "contados-unidades");
    };

    actualizarContador("tabla-seleccionados", "contados-unidades");
    actualizarContador("tabla-unidades", "contador-unidades");
    fila.remove();
}


function actualizarContador(idTabla, idContador) {
    const filasVisibles = document.querySelectorAll(`#${idTabla} tbody tr:not(.d-none)`);
    document.getElementById(idContador).textContent = "[ " + filasVisibles.length + " ]";
}

document.addEventListener("DOMContentLoaded", function () {
    actualizarContador("tabla-unidades", "contador-unidades");
});