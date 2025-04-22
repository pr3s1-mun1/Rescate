document.addEventListener('DOMContentLoaded', function() {
    var imagenes = document.querySelectorAll('.imagen img'); 
    var partesAgregadas = new Set(); 
    var contador = 0; 
    

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
    }
    

    function manejarDobleClick() {
        var parteCuerpo = this.getAttribute('alt');
        var tabla = document.getElementById('tabla-impacto-seleccionadas');
        
        if (partesAgregadas.has(parteCuerpo)) {
            return;
        }
        
        if (!tabla) {
            console.error('No se encontró la tabla con ID "tabla-impacto-seleccionadas"');
            return;
        }
        
        var tbody = tabla.getElementsByTagName('tbody')[0];
        if (!tbody) {
            tbody = document.createElement('tbody');
            tabla.appendChild(tbody);
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
    }
    
    imagenes.forEach(function(imagen) {
        imagen.addEventListener('dblclick', manejarDobleClick);
    });
    
    actualizarContador();
});