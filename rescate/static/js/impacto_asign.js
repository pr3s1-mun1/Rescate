let partesAsig = new Set();
let tablaImpactos;
let inputHidden;

function eliminarFila(fila, parteCuerpo) {
    fila.remove(); 
    partesAsig.delete(parteCuerpo);
    actualizarContador('tabla-impacto-seleccionadas', 'contador-impacto-seleccionadas');
    prepararDatosEnvio();
}

function manejarDobleClickImagen(event) {
    const parteCuerpo = this.getAttribute('alt');
    
    if (partesAsig.has(parteCuerpo)) return;
    
    const tbody = tablaImpactos.querySelector('tbody') || tablaImpactos.appendChild(document.createElement('tbody'));
    const fila = tbody.insertRow();
    fila.setAttribute('data-parte', parteCuerpo);
    
    const celdaParte = fila.insertCell(0);
    celdaParte.textContent = parteCuerpo;
    
    fila.addEventListener('dblclick', function() {
        eliminarFila(fila, parteCuerpo);
    });
    
    partesAsig.add(parteCuerpo);
    actualizarContador('tabla-impacto-seleccionadas', 'contador-impacto-seleccionadas');
    prepararDatosEnvio();
}

function prepararDatosEnvio() {
    const impactos = Array.from(tablaImpactos.querySelectorAll('tbody tr')).map(tr => ({
        descripcion: tr.cells[0]?.textContent.trim() || ""  
    }));
    inputHidden.value = JSON.stringify(impactos);
}

function inicializarImpactos() {
    tablaImpactos = document.getElementById('tabla-impacto-seleccionadas');
    inputHidden = document.getElementById('input-impacto-seleccionadas');

    actualizarContador('tabla-impacto-seleccionadas', 'contador-impacto-seleccionadas');
    if (!tablaImpactos || !inputHidden) {
        console.error('Faltan elementos clave: tabla-impacto-seleccionadas o input-impacto-seleccionadas');
        return;
    }

    const imagenes = document.querySelectorAll('.imagen img'); 
    imagenes.forEach(imagen => {
        imagen.removeEventListener('dblclick', manejarDobleClickImagen);
        imagen.addEventListener('dblclick', manejarDobleClickImagen);
    });

    const filasIniciales = tablaImpactos.querySelectorAll('tbody tr');
    filasIniciales.forEach(fila => {
        const parteCuerpo = fila.cells[0]?.textContent.trim() || "";
        if (!partesAsig.has(parteCuerpo)) {
            partesAsig.add(parteCuerpo);
            fila.addEventListener('dblclick', function () {
                eliminarFila(fila, parteCuerpo);
            });
        }
    });

    prepararDatosEnvio(); 
}

document.addEventListener('DOMContentLoaded', inicializarImpactos);
