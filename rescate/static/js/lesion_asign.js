function agregarParte(descripcion, partesAgregadas, tablaSeleccionados, inputHidden) {
    if (partesAgregadas.has(descripcion)) {
        alert('Esta parte ya está seleccionada');
        return;
    }

    const parteElemento = document.querySelector(`.parte-cuerpo[data-parte="${descripcion}"]`);
    const valor = parteElemento?.getAttribute('data-valor') || "";

    const newRow = document.createElement('tr');
    newRow.dataset.parte = descripcion;
    newRow.dataset.valor = valor;

    newRow.innerHTML = `
        <td>${descripcion}</td>
        <td>${valor}</td>
    `;

    newRow.addEventListener('dblclick', function () {
        eliminarParte(newRow, descripcion, partesAgregadas, tablaSeleccionados, inputHidden);
    });

    tablaSeleccionados.appendChild(newRow);
    partesAgregadas.add(descripcion);

    parteElemento.style.fill = '#d4edda';

    actualizarContador('tabla-partes-seleccionadas', 'contador-partes-seleccionadas');
    actualizarInputHidden(tablaSeleccionados, inputHidden);
}

function eliminarParte(fila, descripcion, partesAgregadas, tablaSeleccionados, inputHidden) {
    fila.remove();
    partesAgregadas.delete(descripcion);
    actualizarContador('tabla-partes-seleccionadas', 'contador-partes-seleccionadas');
    actualizarInputHidden(tablaSeleccionados, inputHidden);

    const parteElemento = document.querySelector(`.parte-cuerpo[data-parte="${descripcion}"]`);
    if (parteElemento) {
        parteElemento.style.fill = "";
    }
}


function actualizarInputHidden(tablaSeleccionados, inputHidden) {
    const partes = Array.from(tablaSeleccionados.querySelectorAll('tr')).map(tr => {
        const descripcion = tr.cells[0]?.textContent.trim() || "";
        const valor = tr.cells[1]?.textContent.trim() || "";
        return { descripcion, valor };
    });
    inputHidden.value = JSON.stringify(partes);
}

document.addEventListener('DOMContentLoaded', function () {
    const tablaSeleccionados = document.querySelector("#tabla-partes-seleccionadas tbody");
    const inputHidden = document.getElementById('input-partes-seleccionadas');
    const partesCuerpo = document.querySelectorAll('.parte-cuerpo');
    const partesAgregadas = new Set();

    partesCuerpo.forEach(parte => {
        parte.addEventListener('dblclick', function () {
            const descripcion = this.getAttribute('data-parte');
            agregarParte(descripcion, partesAgregadas, tablaSeleccionados, inputHidden);
        });
    });

    document.querySelectorAll("#tabla-partes-seleccionadas tbody tr").forEach(fila => {
        const descripcion = fila.cells[0]?.textContent.trim() || "";
        const valor = fila.cells[1]?.textContent.trim() || "";

        fila.addEventListener('dblclick', function () {
            eliminarParte(fila, descripcion, partesAgregadas, tablaSeleccionados, inputHidden);
        });

        const parteElemento = document.querySelector(`.parte-cuerpo[data-parte="${descripcion}"]`);
        if (parteElemento) {
            parteElemento.style.fill = '#d4edda';
        }

        partesAgregadas.add(descripcion);
    });

    actualizarContador('tabla-partes-seleccionadas', 'contador-partes-seleccionadas');
    actualizarInputHidden(tablaSeleccionados, inputHidden);
});
