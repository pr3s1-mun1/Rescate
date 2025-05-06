function actualizarContador(idTabla, idContador) {
    const filasVisibles = document.querySelectorAll(`#${idTabla} tbody tr:not(.d-none)`);
    document.getElementById(idContador).textContent = "[ " + filasVisibles.length + " ]";
}