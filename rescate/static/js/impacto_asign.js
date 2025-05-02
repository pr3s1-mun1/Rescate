document.addEventListener('DOMContentLoaded', function() {
    var imagenes = document.querySelectorAll('.imagen img'); 
    var partesAgregadas = new Set(); 
    var contador = 0; 
    
    // Elementos
    var tablaImpactos = document.getElementById('tabla-impacto-seleccionadas');
    var inputHidden = document.getElementById('input-impacto-seleccionadas'); // input hidden para los impactos

    function actualizarContador() {
        var contadorElement = document.getElementById('contador-impacto-seleccionadas');
        if (contadorElement) {
            contadorElement.textContent = "[ " + contador + " ]";
        }
    }

    /**
     * @param {HTMLTableRowElement} fila 
     * @param {string} parteCuerpo 
     */
    function eliminarFila(fila, parteCuerpo) {
        fila.remove(); 
        partesAgregadas.delete(parteCuerpo); 
        contador--;
        actualizarContador();
        prepararDatosEnvio()
    }

    function manejarDobleClick() {
        var parteCuerpo = this.getAttribute('alt');
        
        if (partesAgregadas.has(parteCuerpo)) {
            return;
        }
        
        if (!tablaImpactos) {
            console.error('No se encontró la tabla con ID "tabla-impacto-seleccionadas"');
            return;
        }
        
        var tbody = tablaImpactos.getElementsByTagName('tbody')[0];
        if (!tbody) {
            tbody = document.createElement('tbody');
            tablaImpactos.appendChild(tbody);
        }
        
        var fila = tbody.insertRow();
        fila.setAttribute('data-parte', parteCuerpo);
        
        var celdaParte = fila.insertCell(0);
        celdaParte.textContent = parteCuerpo;
        
        fila.addEventListener('dblclick', function() {
            eliminarFila(fila, parteCuerpo);
        });
        
        partesAgregadas.add(parteCuerpo);
        contador++;
        actualizarContador();
        prepararDatosEnvio()
    }

    imagenes.forEach(function(imagen) {
        imagen.addEventListener('dblclick', manejarDobleClick);
    });
    
    // Función para preparar el JSON de los impactos seleccionados
    function prepararDatosEnvio() {
        const impactos = Array.from(tablaImpactos.querySelectorAll('tr')).map(
            tr => ({ descripcion: tr.dataset.parte })
        );
        inputHidden.value = JSON.stringify(impactos); // Asignar el JSON al campo oculto
    }

    actualizarContador();
});
