function moverUnidadASeleccionados(fila, clave, descripcion) {
    let tablaSeleccionados = document.getElementById("tabla-seleccionados").getElementsByTagName('tbody')[0];

    let nuevaFila = tablaSeleccionados.insertRow();
    nuevaFila.setAttribute("data-clave", clave);

    let celdaTipo = nuevaFila.insertCell(0);
    celdaTipo.textContent = descripcion;

    let celdaIdUnidad = nuevaFila.insertCell(1);
    let inputIdUnidad = document.createElement("input");
    inputIdUnidad.type = "text";
    inputIdUnidad.className = "form-control";
    inputIdUnidad.name = `id_unidad_${clave}`;
    celdaIdUnidad.appendChild(inputIdUnidad);

    let celdaAgente = nuevaFila.insertCell(2);
    let inputAgente = document.createElement("input");
    inputAgente.type = "text";
    inputAgente.className = "form-control";
    inputAgente.name = `agente_${clave}`;
    celdaAgente.appendChild(inputAgente);

    nuevaFila.ondblclick = function () {
        tablaSeleccionados.deleteRow(nuevaFila.rowIndex - 1);
        actualizarContador("tabla-seleccionados", "contados-unidades");
    };

    actualizarContador("tabla-seleccionados", "contados-unidades");
    actualizarContador("tabla-unidades", "contador-unidades");
}

function actualizarContador(idTabla, idContador) {
    const filasVisibles = document.querySelectorAll(`#${idTabla} tbody tr:not(.d-none)`);
    document.getElementById(idContador).textContent = "[ " + filasVisibles.length + " ]";
}

document.addEventListener("DOMContentLoaded", function () {
    actualizarContador("tabla-unidades", "contador-unidades");
});
