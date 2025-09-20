/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

var confirmationStylesInjected = false;

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
        this._ensureConfirmationStyles();

        var sanitizedSubdomain = $('<div />').text(subdomain).html();

        return new Promise(function (resolve) {
            var resolved = false;
            var previouslyFocused = document.activeElement;

            var $backdrop = $('<div/>', {
                class: 'o-signup-confirmation-backdrop',
            });

            var $dialog = $('<div/>', {
                class: 'o-signup-confirmation-dialog',
                role: 'dialog',
                'aria-modal': 'true',
                'aria-label': 'Confirmación de subdominio',
            });

            var $message = $('<p/>', {
                class: 'o-signup-confirmation-message',
                html:
                    'Se creará la base de datos en <strong>https://' +
                    sanitizedSubdomain +
                    '.factuoo.com</strong>',
            });

            var $subtitle = $('<p/>', {
                class: 'o-signup-confirmation-subtitle',
                text: '¿Deseas continuar o modificar los datos?',
            });

            var $buttons = $('<div/>', { class: 'o-signup-confirmation-actions' });

            var $acceptButton = $('<button/>', {
                type: 'button',
                class: 'o-signup-confirmation-button o-confirm-accept',
                text: 'Aceptar',
            });

            var $modifyButton = $('<button/>', {
                type: 'button',
                class: 'o-signup-confirmation-button o-confirm-modify',
                text: 'Modificar',
            });

            $buttons.append($acceptButton, $modifyButton);
            $dialog.append($message, $subtitle, $buttons);
            $backdrop.append($dialog);

            var resolveOnce = function (value) {
                if (resolved) {
                    return;
                }
                resolved = true;
                if (previouslyFocused && previouslyFocused.focus) {
                    previouslyFocused.focus();
                }
                $backdrop.remove();
                document.removeEventListener('keydown', onKeyDown, true);
                resolve(value);
            };

            var focusable = [$acceptButton[0], $modifyButton[0]];

            var onKeyDown = function (ev) {
                if (ev.key === 'Escape') {
                    ev.preventDefault();
                    resolveOnce(false);
                } else if (ev.key === 'Enter') {
                    ev.preventDefault();
                    resolveOnce(true);
                } else if (ev.key === 'Tab') {
                    if (focusable.length === 0) {
                        return;
                    }
                    ev.preventDefault();
                    var currentIndex = focusable.indexOf(document.activeElement);
                    if (currentIndex === -1) {
                        focusable[0].focus();
                        return;
                    }
                    if (ev.shiftKey) {
                        var previousIndex = (currentIndex - 1 + focusable.length) % focusable.length;
                        focusable[previousIndex].focus();
                    } else {
                        var nextIndex = (currentIndex + 1) % focusable.length;
                        focusable[nextIndex].focus();
                    }
                }
            };

            $acceptButton.on('click', function () {
                resolveOnce(true);
            });

            $modifyButton.on('click', function () {
                resolveOnce(false);
            });

            document.addEventListener('keydown', onKeyDown, true);
            $('body').append($backdrop);
            $acceptButton.trigger('focus');
        });
    },

    _ensureConfirmationStyles: function () {
        if (confirmationStylesInjected) {
            return;
        }

        confirmationStylesInjected = true;

        var styles =
            '.o-signup-confirmation-backdrop {' +
            ' position: fixed;' +
            ' inset: 0;' +
            ' background-color: rgba(0, 0, 0, 0.45);' +
            ' display: flex;' +
            ' align-items: center;' +
            ' justify-content: center;' +
            ' z-index: 1100;' +
            '}' +
            '.o-signup-confirmation-dialog {' +
            ' background-color: #ffffff;' +
            ' border-radius: 12px;' +
            ' padding: 24px 24px 20px;' +
            ' max-width: 420px;' +
            ' width: calc(100% - 32px);' +
            ' box-shadow: 0 20px 60px rgba(0, 0, 0, 0.18);' +
            ' text-align: center;' +
            ' font-family: inherit;' +
            '}' +
            '.o-signup-confirmation-message {' +
            ' font-size: 1.25rem;' +
            ' font-weight: 500;' +
            ' margin: 0 0 12px;' +
            '}' +
            '.o-signup-confirmation-subtitle {' +
            ' margin: 0 0 24px;' +
            ' color: #444444;' +
            ' font-size: 0.95rem;' +
            '}' +
            '.o-signup-confirmation-actions {' +
            ' display: flex;' +
            ' gap: 12px;' +
            ' flex-wrap: wrap;' +
            ' justify-content: center;' +
            '}' +
            '.o-signup-confirmation-button {' +
            ' min-width: 120px;' +
            ' padding: 10px 18px;' +
            ' border-radius: 999px;' +
            ' border: 1px solid transparent;' +
            ' font-size: 0.95rem;' +
            ' cursor: pointer;' +
            ' transition: background-color 0.2s ease, color 0.2s ease, border-color 0.2s ease;' +
            '}' +
            '.o-signup-confirmation-button:focus {' +
            ' outline: 3px solid rgba(41, 128, 185, 0.35);' +
            ' outline-offset: 2px;' +
            '}' +
            '.o-confirm-accept {' +
            ' background-color: #2980b9;' +
            ' color: #ffffff;' +
            '}' +
            '.o-confirm-accept:hover {' +
            ' background-color: #1f6392;' +
            '}' +
            '.o-confirm-modify {' +
            ' background-color: #ffffff;' +
            ' color: #2980b9;' +
            ' border-color: #2980b9;' +
            '}' +
            '.o-confirm-modify:hover {' +
            ' background-color: rgba(41, 128, 185, 0.08);' +
            '}' +
            '.o-signup-confirmation-dialog strong {' +
            ' word-break: break-word;' +
            '}';

        var $style = $('<style/>', { text: styles });
        $style.appendTo('head');
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