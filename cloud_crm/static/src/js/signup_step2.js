/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.ModuleSelectionStep = publicWidget.Widget.extend({
    selector: '#signup_step2_form', 
    start: function () {
        this._bindModuleCheckboxes();
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
});
