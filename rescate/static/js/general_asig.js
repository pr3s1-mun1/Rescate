function actualizarContador(idTabla, idContador) {
    const filasVisibles = document.querySelectorAll(`#${idTabla} tbody tr:not(.d-none)`);
    document.getElementById(idContador).textContent = "[ " + filasVisibles.length + " ]";
}

document.addEventListener("DOMContentLoaded", function () {
    // ==== Campos de emergencia ====
    const coloniaEmergenciaSelect = document.getElementById("id_colonia_emergencia");
    const direccionEmergenciaSelect = document.getElementById("id_direccion_emergencia");
    const cruceEmergenciaSelect = document.getElementById("id_calle_entre");

    if (direccionEmergenciaSelect) {
        direccionEmergenciaSelect.addEventListener("change", function () {
            const calleId = this.value;

            // Limpiar selects si no hay calle
            if (!calleId) {
                if (coloniaEmergenciaSelect) coloniaEmergenciaSelect.innerHTML = '<option value="">---------</option>';
                if (cruceEmergenciaSelect) cruceEmergenciaSelect.innerHTML = '<option value="">---------</option>';
                return;
            }

            // Cargar colonias de emergencia
            fetch('/servicios/ajax/calles_por_colonia/?calle_id=' + calleId)
                .then(res => res.json())
                .then(data => {
                    if (coloniaEmergenciaSelect) {
                        coloniaEmergenciaSelect.innerHTML = '<option value="">---------</option>';
                        data.forEach(col => {
                            const option = document.createElement("option");
                            option.value = col.id;
                            option.textContent = col.nombre;
                            coloniaEmergenciaSelect.appendChild(option);
                        });
                    }
                })
                .catch(err => console.error('Error al cargar colonias de emergencia:', err));

            // Cargar cruces de emergencia
            if (cruceEmergenciaSelect) {
                cruceEmergenciaSelect.innerHTML = '<option value="">---------</option>';
                fetch('/servicios/ajax/calles_por_calle/?calle_id=' + calleId)
                    .then(res => res.json())
                    .then(data => {
                        data.forEach(calle => {
                            const option = document.createElement("option");
                            option.value = calle.id;
                            option.textContent = calle.nombre;
                            cruceEmergenciaSelect.appendChild(option);
                        });
                    })
                    .catch(err => console.error('Error al cargar cruces de emergencia:', err));
            }
        });
    }

    // ==== Campos normales ====
    const coloniaSelect = document.getElementById("id_colonia");
    const domicilioSelect = document.getElementById("id_domicilio");

    if (domicilioSelect) {
        domicilioSelect.addEventListener("change", function () {
            const calleId = this.value;

            // Limpiar selects si no hay calle
            if (!calleId) {
                if (coloniaSelect) coloniaSelect.innerHTML = '<option value="">---------</option>';
                return;
            }

            // Cargar colonias y domicilios normales
            fetch('/servicios/ajax/calles_por_colonia/?calle_id=' + calleId)
                .then(res => res.json())
                .then(data => {
                    if (coloniaSelect) coloniaSelect.innerHTML = '<option value="">---------</option>';

                    data.forEach(item => {
                        if (coloniaSelect) {
                            const optionCol = document.createElement("option");
                            optionCol.value = item.id;
                            optionCol.textContent = item.nombre;
                            coloniaSelect.appendChild(optionCol);
                        }
                        if (domicilioSelect) {
                            const optionDom = document.createElement("option");
                            optionDom.value = item.id;
                            optionDom.textContent = item.nombre;
                            domicilioSelect.appendChild(optionDom);
                        }
                    });
                })
                .catch(err => console.error('Error al cargar colonias/domicilios:', err));
        });
    }
});
