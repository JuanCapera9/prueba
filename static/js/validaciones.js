document.addEventListener('DOMContentLoaded', function () {
    const loginForm = document.getElementById('loginForm');
    const loginCorreo = document.getElementById('loginCorreo');
    const loginContraseña = document.getElementById('loginContraseña');

    const registerForm = document.getElementById('registerForm');
    const registerUsuario = document.getElementById('registerUsuario');
    const registerCorreo = document.getElementById('registerCorreo');
    const registerContraseña = document.getElementById('registerContraseña');

    const emailRegex = /^[a-zA-Z0-9._%+-]+@(gmail\.com|outlook\.com|hotmail\.com)$/;
    const passwordRegex = /^(?=.*[A-Z])[A-Za-z\d@$!%*?&]{8,12}$/;
    const usuarioRegex = /^(?=.*[A-Z])[A-Za-zñÑ\s]{1,}$/;

    function validateInput(input, regex, message) {
        if (regex.test(input.value)) {
            input.classList.add('valid');
            input.classList.remove('invalid');
            input.nextElementSibling.innerHTML = ''; // Limpiar mensaje de error
        } else {
            input.classList.add('invalid');
            input.classList.remove('valid');
            input.nextElementSibling.innerHTML = message;
        }
    }

    loginCorreo.addEventListener('input', function () {
        validateInput(loginCorreo, emailRegex, 'Por favor, introduce un correo electrónico válido.');
        loginContraseña.disabled = !emailRegex.test(loginCorreo.value);
    });

    loginContraseña.addEventListener('input', function () {
        validateInput(loginContraseña, passwordRegex, 'La contraseña debe tener entre 8 y 12 caracteres y al menos una mayúscula.');
    });

    registerUsuario.addEventListener('input', function () {
        validateInput(registerUsuario, usuarioRegex, 'El nombre de usuario debe empezar con mayúscula y contener solo letras.');
    });

    registerCorreo.addEventListener('input', function () {
        validateInput(registerCorreo, emailRegex, 'Por favor, introduce un correo electrónico válido.');
    });

    registerContraseña.addEventListener('input', function () {
        validateInput(registerContraseña, passwordRegex, 'La contraseña debe tener entre 8 y 12 caracteres y al menos una mayúscula.');
    });

    loginForm.addEventListener('submit', function (e) {
        if (!emailRegex.test(loginCorreo.value) || !passwordRegex.test(loginContraseña.value)) {
            e.preventDefault();
            alert('Por favor, introduce datos válidos en el formulario de inicio de sesión.');
        }
    });

    registerForm.addEventListener('submit', function (e) {
        if (!emailRegex.test(registerCorreo.value) || !passwordRegex.test(registerContraseña.value) || !usuarioRegex.test(registerUsuario.value)) {
            e.preventDefault();
            alert('Por favor, introduce datos válidos en el formulario de registro.');
        }
    });
});
