/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.SignupStep1Form = publicWidget.Widget.extend({
    selector: '#signup_step1_form',
    events: {
        'input #name': 'onNameInput',
        'input #company_name': 'onCompanyInput',
        'input #subdomain_input': 'onSubdomainInput',
        'submit': 'onFormSubmit',
        'change #zip_id': 'OnchangeZip',
    },

    start: function () {
        this._subdomainLocked = false;
        this._isProgrammaticUpdate = false;
        this._confirmationShownOnce = false;
        this._skipFurtherConfirmation = false;
        this._subdomainEditedManually = false;
        this._nameField = this.$('#name');
        this._companyField = this.$('#company_name');
        this._subdomainField = this.$('#subdomain_input');

        this._initZipSelect2();

        if (!this._subdomainField.val()) {
            if (this._companyField.val()) {
                this._updateSubdomainSuggestion('company');
            } else {
                this._updateSubdomainSuggestion('name');
            }
        }

        return this._super.apply(this, arguments);
    },

    onNameInput: function () {
        this._updateSubdomainSuggestion('name');
    },

    onCompanyInput: function () {
        this._updateSubdomainSuggestion('company');
    },

    onSubdomainInput: function () {
        if (this._isProgrammaticUpdate) {
            return;
        }
        this._subdomainLocked = true;
        this._subdomainEditedManually = true;
        if (this._confirmationShownOnce) {
            this._skipFurtherConfirmation = true;
        }
    },

    onFormSubmit: function (ev) {
        if (this._skipFurtherConfirmation) {
            return;
        }

        var subdomain = (this._subdomainField.val() || '').trim();
        if (!subdomain) {
            return;
        }

        if (subdomain.length < 3) {
            ev.preventDefault();
            if (this._subdomainField[0] && this._subdomainField[0].setCustomValidity) {
                this._subdomainField[0].setCustomValidity('El subdominio debe contener al menos 3 caracteres.');
                this._subdomainField[0].reportValidity();
            } else {
                window.alert('El subdominio debe contener al menos 3 caracteres.');
            }
            return;
        }

        if (this._subdomainField[0] && this._subdomainField[0].setCustomValidity) {
            this._subdomainField[0].setCustomValidity('');
        }

        ev.preventDefault();
        this._confirmationShownOnce = true;

        var self = this;
        this._showConfirmationDialog(subdomain).then(function (confirmed) {
            if (!confirmed) {
                return;
            }

            self._skipFurtherConfirmation = true;
            self.el.submit();
        });
    },

    _updateSubdomainSuggestion: function (source) {
        if (this._subdomainLocked) {
            return;
        }

        var baseValue = '';
        if (source === 'company') {
            baseValue = (this._companyField.val() || '').trim();
            if (!baseValue) {
                if (!this._subdomainEditedManually) {
                    var nameFallback = (this._nameField.val() || '').trim();
                    if (nameFallback) {
                        var fallbackSuggestion = this._buildSubdomainCandidate(nameFallback);
                        this._setSubdomainValue(fallbackSuggestion);
                    } else {
                        this._setSubdomainValue('');
                    }
                }
                return;
            }
        } else {
            baseValue = (this._nameField.val() || '').trim();
            if (!baseValue) {
                baseValue = (this._companyField.val() || '').trim();
                if (!baseValue) {
                    return;
                }
            }
        }

        var suggestion = this._buildSubdomainCandidate(baseValue);
        if (!suggestion && source === 'name') {
            suggestion = this._buildSubdomainCandidate((this._companyField.val() || '').trim());
        }

        if (suggestion) {
            this._setSubdomainValue(suggestion);
        }
    },

    _buildSubdomainCandidate: function (value) {
        if (!value) {
            return '';
        }

        var normalized = value;
        if (normalized.normalize) {
            normalized = normalized.normalize('NFD').replace(/[\u0300-\u036f]/g, '');
        }

        var words = normalized.split(/\s+/).filter(Boolean);
        var candidate = '';

        if (words.length >= 2 && words[0].length >= 5) {
            candidate = words[0];
        } else {
            candidate = normalized.replace(/\s+/g, '');
        }

        candidate = candidate.toLowerCase().replace(/[^a-z0-9\-]/g, '');
        return candidate.substring(0, 20);
    },

    _setSubdomainValue: function (value) {
        if (!this._subdomainField.length) {
            return;
        }

        this._isProgrammaticUpdate = true;
        this._subdomainField.val(value);
        this._isProgrammaticUpdate = false;

        if (this._subdomainField[0] && this._subdomainField[0].setCustomValidity) {
            this._subdomainField[0].setCustomValidity('');
        }
    },

    _showConfirmationDialog: function (subdomain) {
        var sanitizedSubdomain = $('<div />').text(subdomain).html();
        var $modal = $(
            '<div class="modal fade o-signup-confirmation-modal" tabindex="-1" role="dialog">' +
                '<div class="modal-dialog modal-dialog-centered" role="document">' +
                    '<div class="modal-content">' +
                        '<div class="modal-body text-center">' +
                            '<p class="mb-3" style="font-size: 1.25rem;">' +
                                'Se creará la base de datos en <strong>https://' +
                                sanitizedSubdomain +
                                '.factuoo.com</strong>' +
                            '</p>' +
                            '<p class="mb-0">¿Deseas continuar o modificar los datos?</p>' +
                        '</div>' +
                        '<div class="modal-footer justify-content-center">' +
                            '<button type="button" class="btn btn-primary o-confirm-accept">Aceptar</button>' +
                            '<button type="button" class="btn btn-secondary o-confirm-modify" data-dismiss="modal">Modificar</button>' +
                        '</div>' +
                    '</div>' +
                '</div>' +
            '</div>'
        );

        return new Promise(function (resolve) {
            var resolved = false;

            var cleanup = function () {
                $modal.remove();
            };

            $modal.on('click', '.o-confirm-accept', function () {
                if (!resolved) {
                    resolved = true;
                    resolve(true);
                }
                $modal.modal('hide');
            });

            $modal.on('click', '.o-confirm-modify', function () {
                if (!resolved) {
                    resolved = true;
                    resolve(false);
                }
                $modal.modal('hide');
            });

            $modal.on('hidden.bs.modal', function () {
                if (!resolved) {
                    resolved = true;
                    resolve(false);
                }
                cleanup();
            });

            $modal.on('shown.bs.modal', function () {
                $modal.find('.o-confirm-accept').trigger('focus');
            });

            $modal.appendTo('body');
            $modal.modal({ backdrop: 'static', keyboard: false, show: true });
        });
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
    },

    OnchangeZip: function (ev) {
        var $zip = this.$('#zip_id');
        var $city = this.$('#city');

        if (!$zip.length) return;

        var selectedData = $zip.select2('data');

        var data = Array.isArray(selectedData) ? selectedData[0] : selectedData;

        if (data && data.text) {
            var parts = data.text.trim().split(' ');
            var cityName = parts.slice(1).join(' ');
            $city.val(cityName);
        } else {
            $city.val('');
        }
    },

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