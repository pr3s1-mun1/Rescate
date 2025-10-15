// Efecto de carga suave para las tarjetas
document.addEventListener('DOMContentLoaded', () => {
    const cards = document.querySelectorAll('.servicio-card');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
    });
});



// Función para cambiar entre pestañas
function changeTab(tabId) {
    // Ocultar todos los contenidos de pestañas
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    
    // Mostrar el contenido de la pestaña seleccionada
    document.getElementById(tabId).classList.add('active');
    
    // Actualizar las pestañas activas
    document.querySelectorAll('.tab').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Marcar la pestaña seleccionada como activa
    event.currentTarget.classList.add('active');
}