document.addEventListener('DOMContentLoaded', function() {
            // Toggle password visibility
            const toggleButtons = document.querySelectorAll('.toggle-password');
            
            toggleButtons.forEach(button => {
                button.addEventListener('click', function() {
                    const passwordInput = this.parentElement.querySelector('input');
                    const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
                    passwordInput.setAttribute('type', type);
                    
                    const icon = this.querySelector('i');
                    if (icon) {
                        icon.classList.toggle('bi-eye');
                        icon.classList.toggle('bi-eye-slash');
                    }
                });
            });

            // Real-time validation
            const form = document.getElementById('form-registro');
            const inputs = form.querySelectorAll('input');
            
            inputs.forEach(input => {
                input.addEventListener('input', function() {
                    validateField(this);
                });
                
                input.addEventListener('blur', function() {
                    validateField(this);
                });
            });
            
            // Form submission
            form.addEventListener('submit', function(event) {
                let formIsValid = true;
                
                inputs.forEach(input => {
                    if (!validateField(input)) {
                        formIsValid = false;
                    }
                });
                
                // Validate password match
                const password = document.getElementById('password').value;
                const confirmPassword = document.getElementById('confirm_password').value;
                
                if (password !== confirmPassword) {
                    document.getElementById('confirm_password-error').textContent = 'Las contraseñas no coinciden';
                    document.getElementById('confirm_password').classList.add('error');
                    formIsValid = false;
                }
                
                if (!formIsValid) {
                    event.preventDefault();
                }
            });
            
            function validateField(field) {
                const errorElement = document.getElementById(`${field.id}-error`);
                
                if (field.required && field.value.trim() === '') {
                    errorElement.textContent = 'Este campo es obligatorio';
                    field.classList.add('error');
                    return false;
                }
                
                // Specific validations
                if (field.id === 'email' && field.value.trim() !== '') {
                    const emailPattern = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}$/;
                    if (!emailPattern.test(field.value)) {
                        errorElement.textContent = 'Por favor ingrese un correo válido';
                        field.classList.add('error');
                        return false;
                    }
                }
                
                if (field.id === 'password' && field.value.trim() !== '' && field.value.length < 8) {
                    errorElement.textContent = 'La contraseña debe tener al menos 8 caracteres';
                    field.classList.add('error');
                    return false;
                }

                if (field.id === 'dni' && field.value.length < 8) {
                    errorElement.textContent = 'El dni debe contener 8 caracteres';
                    field.classList.add('error');
                    return false;
                }
                
                // Clear error if valid
                errorElement.textContent = '';
                field.classList.remove('error');
                return true;
            }
        });