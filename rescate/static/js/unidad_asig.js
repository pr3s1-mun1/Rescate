function moverUnidadASeleccionados(fila, clave, descripcion) {
    const yaSeleccionado = document.querySelector(`#tabla-seleccionados tbody tr[data-clave="${clave}"]`);
    if (yaSeleccionado) return;

    let tablaSeleccionados = document.getElementById("tabla-seleccionados").getElementsByTagName('tbody')[0];

    let nuevaFila = tablaSeleccionados.insertRow();

    let celdaClave = nuevaFila.insertCell(0);
    celdaClave.textContent = clave;
    celdaClave.setAttribute("hidden", true)

    let celdaTipo = nuevaFila.insertCell(1);
    celdaTipo.textContent = descripcion;

    let celdaIdUnidad = nuevaFila.insertCell(2);
    let inputIdUnidad = document.createElement("input");
    inputIdUnidad.type = "text";
    inputIdUnidad.className = "form-control";
    celdaIdUnidad.appendChild(inputIdUnidad);

    let celdaAgente = nuevaFila.insertCell(3);
    let inputAgente = document.createElement("input");
    inputAgente.type = "text";
    inputAgente.className = "form-control";
    celdaAgente.appendChild(inputAgente);

    inputIdUnidad.addEventListener("input", llenarInputs);
    inputAgente.addEventListener("input", llenarInputs);

    nuevaFila.ondblclick = function () {
        tablaSeleccionados.deleteRow(nuevaFila.rowIndex - 1);
        llenarInputs();
        actualizarContador("tabla-seleccionados", "contados-unidades");
    };

    llenarInputs();

    actualizarContador("tabla-seleccionados", "contados-unidades");
    actualizarContador("tabla-unidades", "contador-unidades");
}

function llenarInputs() {
    const tabla = document.getElementById("tabla-seleccionados");
    if (!tabla) return;

    const filas = tabla.querySelectorAll("tbody tr");
    const unidades = [];

    filas.forEach(fila => {
        const clave = fila.querySelector("td:nth-child(1)")?.textContent.trim() || "";
        const id_unidad = fila.querySelector("td:nth-child(3) input")?.value.trim() || "";
        const agente = fila.querySelector("td:nth-child(4) input")?.value.trim() || "";  
        
        unidades.push({
            clave,
            id_unidad,
            agente
        });
    });

    const inputHidden = document.getElementById("input-unidades");
    if (inputHidden) {
        inputHidden.value = JSON.stringify(unidades);
    }
}

document.addEventListener("DOMContentLoaded", function () {

    actualizarContador("tabla-unidades", "contador-unidades");
    actualizarContador("tabla-seleccionados", "contados-unidades");
    llenarInputs();
});
