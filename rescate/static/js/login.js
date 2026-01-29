// Toggle de contraseña
const togglePassword = document.getElementById('togglePassword');
const passwordInput = document.getElementById('contrasena');

togglePassword.addEventListener('click', function() {
    const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
    passwordInput.setAttribute('type', type);
    this.classList.toggle('fa-eye');
    this.classList.toggle('fa-eye-slash');
});

// Efecto de carga al enviar
const loginForm = document.getElementById('loginForm');
const submitBtn = document.getElementById('submitBtn');

loginForm.addEventListener('submit', function(e) {
    submitBtn.classList.add('loading');
    submitBtn.innerHTML = '';
    submitBtn.disabled = true;
});

// Año actual
document.getElementById('currentYear').textContent = new Date().getFullYear();

// Validación básica
loginForm.addEventListener('submit', function(e) {
    const usuario = document.getElementById('usuario').value.trim();
    const contrasena = document.getElementById('contrasena').value.trim();
    
    if (!usuario || !contrasena) {
        e.preventDefault();
        alert('Por favor complete todos los campos');
        submitBtn.classList.remove('loading');
        submitBtn.innerHTML = '<i class="fas fa-sign-in-alt"></i> Acceder al sistema';
        submitBtn.disabled = false;
    }
});

// Efecto de enfoque en campos
const inputs = document.querySelectorAll('.form-input');
inputs.forEach(input => {
    input.addEventListener('focus', function() {
        this.parentElement.querySelector('i').style.color = 'var(--primary)';
    });
    
    input.addEventListener('blur', function() {
        this.parentElement.querySelector('i').style.color = 'var(--primary)';
    });
});

// Forzar recarga siempre que se abra el login
window.addEventListener('load', () => {
    // Se recarga la página una vez
    if (!sessionStorage.getItem('loginReloaded')) {
        sessionStorage.setItem('loginReloaded', 'true');
        location.reload();
    } else {
        sessionStorage.removeItem('loginReloaded');
    }
});