/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.ModuleSelectionStep = publicWidget.Widget.extend({
    selector: '#signup_step2_form',
    start: function () {
        this._bindModuleCheckboxes();
        this._bindFormSubmission();
        return this._super.apply(this, arguments);
    },

    _bindModuleCheckboxes: function () {
        const self = this;
        this.$('input[name="modules"]').each(function () {
            $(this).on('change', function (event) {
                self._toggleModuleSelection(event.currentTarget);
            });
        });
    },

    _toggleModuleSelection: function (checkbox) {
        const $box = $(checkbox).closest('.module-box');
        if ($box.length) {
            if (checkbox.checked) {
                $box.addClass('selected');
            } else {
                $box.removeClass('selected');
            }
        }
    },

    _bindFormSubmission: function () {
        const self = this;
        this.$el.on('submit', function () {
            const $submitButton = self.$('button[type="submit"]');
            $('body').addClass('cursor-wait');
            $submitButton.prop('disabled', true).addClass('is-processing');

            window.addEventListener(
                'pageshow',
                function () {
                    $('body').removeClass('cursor-wait');
                    $submitButton.prop('disabled', false).removeClass('is-processing');
                },
                { once: true }
            );
        });
    },
});
