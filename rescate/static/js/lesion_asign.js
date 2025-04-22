document.addEventListener('DOMContentLoaded', function() {
    const tablaSeleccionados = document.querySelector("#tabla-partes-seleccionadas tbody");
    const contador = document.getElementById('contador-partes-seleccionadas');
    const inputHidden = document.getElementById('input-partes-seleccionadas');
    const partesCuerpo = document.querySelectorAll('.parte-cuerpo');

    const partesAgregadas = new Set();

    /**
     * @param {string} descripcion
     */
    function agregarParte(descripcion) {
        if (partesAgregadas.has(descripcion)) {
            alert('Esta parte ya está seleccionada');
            return;
        }

        const newRow = document.createElement('tr');
        newRow.dataset.parte = descripcion;
        newRow.innerHTML = `
            <td>${tablaSeleccionados.children.length + 1}</td>
            <td>${descripcion}</td>
        `;

        newRow.addEventListener('dblclick', function() {
            eliminarParte(this, descripcion);
        });

        tablaSeleccionados.appendChild(newRow);
        partesAgregadas.add(descripcion);
        
        actualizarContador();
        actualizarInputHidden();
    }

    /**
     * @param {HTMLTableRowElement} fila 
     * @param {string} descripcion 
     */
    function eliminarParte(fila, descripcion) {
        fila.remove();
        partesAgregadas.delete(descripcion);
        reordenarNumeracion();
        actualizarContador();
        actualizarInputHidden();
    }

    function reordenarNumeracion() {
        const filas = tablaSeleccionados.querySelectorAll('tr');
        filas.forEach((fila, index) => {
            fila.querySelector('td:first-child').textContent = index + 1;
        });
    }

    function actualizarContador() {
        contador.textContent = "[ " + tablaSeleccionados.children.length + " ]";
    }

    function actualizarInputHidden() {
        const partes = Array.from(tablaSeleccionados.querySelectorAll('tr')).map(
            tr => tr.querySelector('td:nth-child(2)').textContent
        );
        inputHidden.value = JSON.stringify(partes);
    }

    partesCuerpo.forEach(parte => {
        parte.addEventListener('dblclick', function() {
            const descripcion = this.getAttribute('data-parte');
            agregarParte(descripcion);
            
            this.style.fill = '#d4edda';
        });
    });

    actualizarInputHidden();
});