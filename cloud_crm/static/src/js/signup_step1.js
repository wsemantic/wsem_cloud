/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.SignupStep1Form = publicWidget.Widget.extend({
    selector: '#signup_step1_form',
    events: {
        'input #company_name': 'updateSubdomain',
    },

    start: function () {
        this._initZipSelect2();
        return this._super.apply(this, arguments);
    },

    updateSubdomain: function () {
        var companyField = this.$('#company_name');
        var subdomainField = this.$('#subdomain_input');
        if (companyField && subdomainField) {
            // Obtener el nombre de la empresa y eliminar espacios al inicio y final
            var companyName = companyField.val().trim();

			// Dividir el nombre de la empresa en palabras
			var words = companyName.split(/\s+/);

            var subdomain = '';

			if (words.length >= 2 && words[0].length >= 5) {
				// Usar la primera palabra como subdominio
				subdomain = words[0];
			} else {
				// Eliminar espacios y limitar a 7 caracteres
				subdomain = companyName.replace(/\s+/g, '').substring(0, 7);
			}

			// Convertir a minúsculas
			subdomain = subdomain.toLowerCase();

			// Eliminar caracteres no alfanuméricos ni guiones
			subdomain = subdomain.replace(/[^a-z0-9\-]/g, '');

            // Establecer el valor del campo subdominio
            subdomainField.val(subdomain) ;
        }
    },

    _initZipSelect2: function () {
        var $zip = this.$('#zip_id');
        if (!$zip.length) return;

        $zip.select2({
            width: '100%',
            placeholder: 'Search Zip...',
            allowClear: true,
            tokenSeparators: [","],
            maximumSelectionSize: 1,
            minimumInputLength: 0,
            ajax: {
                url: "/get_zip_list",
                quietMillis: 600,
                dataType: 'json',
                data: function (term, page) {
                    return {
                        searchTerm: term || '',
                        page: page || 1,
                        pageSize: 20,
                    };
                },
                results: function (data, page) {
                    return {
                        results: data.map(function (x) {
                            return { id: x.id, text: x.name };
                        }),
                        more: data.length === 20,
                    };
                },
            },
        });
    }

});

// Incluir la funcionalidad select2 en el campo de código postal
// $(document).ready(function() {
//     $('#zip_id').select2({
//         width: '100%',
//         placeholder: 'Search Zip...',
//         allowClear: true,
//         tokenSeparators: [","],
//         maximumSelectionSize: 1,
//         minimumInputLength: 0,
//         ajax: {
//             url: "/get_zip_list",
//             quietMillis: 600,
//             dataType: 'json',
//             data: function(term, page) {
//                 console.log(page)
//                 return {
//                     searchTerm: term || '',
//                     page: page || 1,
//                     pageSize: 20
//                 };
//             },
//             results: function(data, page) {
//                 var results = data.map(function(x) {
//                     return {
//                         id: x.id,
//                         text: x.name,
//                     };
//                 });
//                 return {
//                     results: results,
//                     more: data.length === 20 
//                 };
//             },
//         },
//     });
// });