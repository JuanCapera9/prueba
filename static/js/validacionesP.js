document.addEventListener('DOMContentLoaded', function () {
    var form = document.getElementById('formAgregarProducto');
    var inputs = form.querySelectorAll('input, select');
    
    var regexPatterns = {
        referencia: /^[A-Z0-9]{3,}$/,
        nombre: /^[a-zA-Z0-9\s]+$/,
        // Añade aquí las demás expresiones regulares necesarias
    };

    function validateField(field) {
        var value = field.value.trim();
        var id = field.id;
        var valid = regexPatterns[id].test(value);

        var icono = field.parentNode.querySelector('.validacion-icono');
        if (valid) {
            icono.innerHTML = '<i class="fas fa-check-circle text-success"></i>';
            field.classList.remove('campo-invalido');
        } else {
            icono.innerHTML = '<i class="fas fa-times-circle text-danger"></i>';
            field.classList.add('campo-invalido');
        }

        return valid;
    }

    inputs.forEach(function(input) {
        input.addEventListener('input', function() {
            validateField(input);
        });
    });

    form.addEventListener('submit', function(event) {
        var valid = true;
        inputs.forEach(function(input) {
            if (!validateField(input)) {
                valid = false;
            }
        });

        if (!valid) {
            event.preventDefault();
            document.getElementById('mensajeError').style.display = 'block';
        } else {
            document.getElementById('mensajeError').style.display = 'none';
        }
    });

    // Mostrar/Ocultar formulario
    document.getElementById('mostrarFormularioBtn').addEventListener('click', function() {
        document.getElementById('agregarProductoForm').style.display = 'block';
    });
    document.getElementById('cerrarFormularioBtn').addEventListener('click', function() {
        document.getElementById('agregarProductoForm').style.display = 'none';
    });
});