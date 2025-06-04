function actualizarContador(idTabla, idContador) {
    const filasVisibles = document.querySelectorAll(`#${idTabla} tbody tr:not(.d-none)`);
    document.getElementById(idContador).textContent = "[ " + filasVisibles.length + " ]";
}

document.addEventListener("DOMContentLoaded", function () {
    const coloniaSelect = document.getElementById("id_colonia_emergencia");
    const direccionSelect = document.getElementById("id_direccion_emergencia");
    const cruceSelect = document.getElementById("id_calle_entre");

    if (coloniaSelect) {
        coloniaSelect.addEventListener("change", function () {
            const coloniaId = this.value;

            fetch('/servicios/ajax/calles_por_colonia/?colonia_id=' + coloniaId)
                .then(response => response.json())
                .then(data => {
                    // Limpiar opciones anteriores
                    direccionSelect.innerHTML = '<option value="">---------</option>';
                    cruceSelect.innerHTML = '<option value="">---------</option>';

                    // Agregar nuevas calles en ambos selects
                    data.forEach(calle => {
                        const option1 = document.createElement("option");
                        option1.value = calle.id;
                        option1.textContent = calle.nombre;
                        direccionSelect.appendChild(option1);

                        const option2 = document.createElement("option");
                        option2.value = calle.id;
                        option2.textContent = calle.nombre;
                        cruceSelect.appendChild(option2);
                    });
                })
                .catch(error => {
                    console.error('Error al cargar calles:', error);
                });
        });
    }
});
