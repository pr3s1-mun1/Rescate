document.addEventListener("DOMContentLoaded", function() {
    const selectAcompanante = document.getElementById("id_tiene_acompanante");
    const camposAcompanante = document.getElementById("campos-acompanante");

    const selectPertenencias = document.getElementById("id_entregan_pertenencias");
    const camposPertenencias = document.getElementById("campos-pertenencias");

    function actualizarVisibilidad() {
        // Mostrar/ocultar campos acompañante
        if (selectAcompanante.value === "1" || selectAcompanante.value.toLowerCase() === "true") {
            camposAcompanante.style.display = "flex"; // o "block" según tu CSS
        } else {
            camposAcompanante.style.display = "none";
            camposAcompanante.querySelectorAll("input, select").forEach(input => {
                input.value = "";
            });
        }

        // Mostrar/ocultar campos pertenencias
        if (selectPertenencias && (selectPertenencias.value === "1" || selectPertenencias.value.toLowerCase() === "true")) {
            camposPertenencias.style.display = "flex";
        } else if (camposPertenencias) {
            camposPertenencias.style.display = "none";
            camposPertenencias.querySelectorAll("input, select, textarea").forEach(input => {
                input.value = "";
            });
        }
    }

    selectAcompanante.addEventListener("change", actualizarVisibilidad);

    if (selectPertenencias) {
        selectPertenencias.addEventListener("change", actualizarVisibilidad);
    }

    actualizarVisibilidad(); // Inicializar al cargar la página
});
