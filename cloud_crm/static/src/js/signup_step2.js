// JavaScript para el segundo paso (gestión de la selección de módulos)
document.addEventListener('DOMContentLoaded', function () {
    // Función para alternar la selección visual del módulo
    function toggleModuleSelection(event) {
        var moduleCheckbox = event.target;
        var moduleBox = moduleCheckbox.closest('.module-box');

        if (moduleBox) {
            if (moduleCheckbox.checked) {
                moduleBox.classList.add('selected');
            } else {
                moduleBox.classList.remove('selected');
            }
        }
    }

    // Obtener todos los checkboxes de los módulos
    var moduleCheckboxes = document.querySelectorAll('input[name="modules"]');

    // Asignar el evento 'change' a cada checkbox de módulo
    moduleCheckboxes.forEach(function (checkbox) {
        checkbox.addEventListener('change', toggleModuleSelection);
    });
});
