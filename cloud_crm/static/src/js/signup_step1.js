// JavaScript para el primer paso (cálculo dinámico del subdominio)
document.addEventListener('DOMContentLoaded', function () {
    // Función para actualizar el subdominio dinámicamente
    function updateSubdomain() {
        var companyField = document.getElementById('company_name');
        var subdomainField = document.getElementById('subdomain_url');

        if (companyField && subdomainField) {
            // Obtener el nombre de la empresa y eliminar espacios al inicio y final
            var companyName = companyField.value.trim();

            // Reemplazar espacios, eliminar caracteres especiales y convertir a minúsculas
            var subdomain = companyName
                .replace(/\s+/g, '')             // Eliminar espacios
                .replace(/[^a-zA-Z0-9\-]/g, '') // Eliminar caracteres especiales
                .toLowerCase();

            // Establecer el valor del campo subdominio
            subdomainField.value = subdomain ? subdomain + '.factuoo.com' : '';
        }
    }

    // Asignar la función al evento 'input' del campo 'company_name'
    var companyInput = document.getElementById('company_name');
    if (companyInput) {
        companyInput.addEventListener('input', updateSubdomain);
    }
});
