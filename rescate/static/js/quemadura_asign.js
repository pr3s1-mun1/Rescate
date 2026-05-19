function agregarQuemadura(descripcion, quemadurasAgregadas, tablaQuemaduras, inputQuemadurasHidden) {
    if (quemadurasAgregadas.has(descripcion)) {
        alert('Esta parte ya está seleccionada');
        return;
    }

    const parteElemento = document.querySelector(`.parte-cuerpo-quem[data-parte="${descripcion}"]`);
    const valor = parteElemento?.getAttribute('data-valor') || "";

    const newRow = document.createElement('tr');
    newRow.dataset.parte = descripcion;
    newRow.dataset.valor = valor;

    newRow.innerHTML = `
        <td>${descripcion}</td>
        <td>${valor}</td>
    `;

    newRow.addEventListener('dblclick', function () {
        eliminarQuemadura(newRow, descripcion, quemadurasAgregadas, tablaQuemaduras, inputQuemadurasHidden);
    });

    tablaQuemaduras.appendChild(newRow);
    quemadurasAgregadas.add(descripcion);

    parteElemento.style.fill = '#f8d7da';

    actualizarContador('tabla-quemaduras-seleccionadas', 'contador-quemaduras-seleccionadas');
    actualizarQuemadurasInputHidden(tablaQuemaduras, inputQuemadurasHidden);
}

function eliminarQuemadura(fila, descripcion, quemadurasAgregadas, tablaQuemaduras, inputQuemadurasHidden) {
    fila.remove();
    quemadurasAgregadas.delete(descripcion);
    actualizarContador('tabla-quemaduras-seleccionadas', 'contador-quemaduras-seleccionadas');
    actualizarQuemadurasInputHidden(tablaQuemaduras, inputQuemadurasHidden);

    const parteElemento = document.querySelector(`.parte-cuerpo-quem[data-parte="${descripcion}"]`);
    if (parteElemento) {
        parteElemento.style.fill = "";
    }
}

function actualizarQuemadurasInputHidden(tablaQuemaduras, inputQuemadurasHidden) {
    const partes = Array.from(tablaQuemaduras.querySelectorAll('tr')).map(tr => {
        const descripcion = tr.cells[0]?.textContent.trim() || "";
        const valor = tr.cells[1]?.textContent.trim() || "";
        return { descripcion, valor };
    });
    inputQuemadurasHidden.value = JSON.stringify(partes);
}

document.addEventListener('DOMContentLoaded', function () {
    const tablaQuemaduras = document.querySelector("#tabla-quemaduras-seleccionadas tbody");
    const inputQuemadurasHidden = document.getElementById('input-quemaduras-seleccionadas');
    const partesCuerpo = document.querySelectorAll('.parte-cuerpo-quem');
    const quemadurasAgregadas = new Set();

    partesCuerpo.forEach(parte => {
        parte.addEventListener('dblclick', function () {
            const descripcion = this.getAttribute('data-parte');
            agregarQuemadura(descripcion, quemadurasAgregadas, tablaQuemaduras, inputQuemadurasHidden);
        });
    });

    document.querySelectorAll("#tabla-quemaduras-seleccionadas tbody tr").forEach(fila => {
        const descripcion = fila.cells[0]?.textContent.trim() || "";
        const valor = fila.cells[1]?.textContent.trim() || "";

        fila.addEventListener('dblclick', function () {
            eliminarQuemadura(fila, descripcion, quemadurasAgregadas, tablaQuemaduras, inputQuemadurasHidden);
        });

        const parteElemento = document.querySelector(`.parte-cuerpo-quem[data-parte="${descripcion}"]`);
        if (parteElemento) {
            parteElemento.style.fill = '#f8d7da';
        }

        quemadurasAgregadas.add(descripcion);
    });

    actualizarContador('tabla-quemaduras-seleccionadas', 'contador-quemaduras-seleccionadas');
    actualizarQuemadurasInputHidden(tablaQuemaduras, inputQuemadurasHidden);
});
