

SKIPOLE.radio = {};


SKIPOLE.radio.RadioButton1 = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    };
SKIPOLE.radio.RadioButton1.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.radio.RadioButton1.prototype.constructor = SKIPOLE.radio.RadioButton1;
SKIPOLE.radio.RadioButton1.prototype.setvalues = function (fieldlist, result) {
    if (!this.widg_id) {
        return;
        }
    /* check if an error message or clear_error is given */
    this.check_error(fieldlist, result);
    // radio_checked
    var radio_checked_value = this.fieldarg_in_result('radio_checked', result, fieldlist);
    if (radio_checked_value) {
        this.widg.find('[value="' + radio_checked_value + '"]').prop('checked', true);
        }
    };



SKIPOLE.radio.RadioTable = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    };
SKIPOLE.radio.RadioTable.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.radio.RadioTable.prototype.constructor = SKIPOLE.radio.RadioTable;



SKIPOLE.radio.TwoRadioOptions = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    this.display_errors = false;
    };
SKIPOLE.radio.TwoRadioOptions.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.radio.TwoRadioOptions.prototype.constructor = SKIPOLE.radio.TwoRadioOptions;


SKIPOLE.radio.BooleanRadio = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    this.display_errors = false;
    };
SKIPOLE.radio.BooleanRadio.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.radio.BooleanRadio.prototype.constructor = SKIPOLE.radio.BooleanRadio;


