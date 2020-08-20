

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


SKIPOLE.radio.RadioTable2 = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    };
SKIPOLE.radio.RadioTable2.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.radio.RadioTable2.prototype.constructor = SKIPOLE.radio.RadioTable2;
SKIPOLE.radio.RadioTable2.prototype.setvalues = function (fieldlist, result) {
    if (!this.widg_id) {
        return;
        }
    var the_widg = this.widg;
    // columns
    var col1 = this.fieldarg_in_result('col1', result, fieldlist);
    var col2 = this.fieldarg_in_result('col2', result, fieldlist);
    var row_classes = this.fieldarg_in_result('row_classes', result, fieldlist);
    var itemchecked = this.fieldarg_in_result('radio_checked', result, fieldlist);
    var index = 0;
    var header = false;
    if (the_widg.find('th').length) {
        header = true;
        }
    the_widg.find('tr').each(function() {
        if (header) {
            // the header line
            header = false;
            }
        else {
            // for each row
            // set its class
            if (row_classes && row_classes.length) {
                $(this).attr("class", row_classes[index]);
                }
            var cells = $(this).children();
            if (col1 && col1.length) {
                $(cells[0]).text(col1[index]);
                 }
            if (col2 && col2.length) {
                $(cells[1]).text(col2[index]);
                 }
            if (itemchecked) {
                // Remove checked status from all rows
                let inputtag = $(cells[2]).find('input')
                inputtag.prop('checked', false);
                let cellval = inputtag.val();
                if (itemchecked == cellval) {
                    inputtag.prop('checked', true);
                    }
                 }
             index=index+1;
            }
        })
    };




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


