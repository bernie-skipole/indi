

SKIPOLE.inputtables = {};


SKIPOLE.inputtables.InputTable1 = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    };
SKIPOLE.inputtables.InputTable1.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.inputtables.InputTable1.prototype.constructor = SKIPOLE.inputtables.InputTable1;
SKIPOLE.inputtables.InputTable1.prototype.setvalues = function (fieldlist, result) {
    if (!this.widg_id) {
        return;
        }
    var the_widg = this.widg;
    // columns
    var col1 = this.fieldarg_in_result('col1', result, fieldlist);
    var col2 = this.fieldarg_in_result('col2', result, fieldlist);
    var row_classes = this.fieldarg_in_result('row_classes', result, fieldlist);
    var keysvals = this.fieldarg_in_result('inputdict', result, fieldlist);
    if (keysvals && Object.keys(keysvals).length) {
        var keysonly = Object.keys(keysvals);
        }
    var self = this;
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
            if (keysonly && keysonly.length) {
                let rowkey = keysonly[index];
                if (rowkey) {
                    // set name attribute and val attribute for each input field
                    let inputtag = $(cells[2]).find('input');
                    inputtag.prop('name', self.formname('inputdict') + "-" + rowkey);
                    inputtag.val(keysvals[rowkey]);
                    }
                 }
             index=index+1;
             
            }
        })
    };



SKIPOLE.inputtables.InputTable5 = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    this.display_errors = false;
    };
SKIPOLE.inputtables.InputTable5.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.inputtables.InputTable5.prototype.constructor = SKIPOLE.inputtables.InputTable5;
SKIPOLE.inputtables.InputTable5.prototype.eventfunc = function(e) {
     var selected_form = $(e.target);
    if (!SKIPOLE.form_validate(selected_form)) {
        // prevent the submission if validation failure
        e.preventDefault();
        }
    };
SKIPOLE.inputtables.InputTable5.prototype.setvalues = function (fieldlist, result) {
    if (!this.widg_id) {
        return;
        }
    var the_widg = this.widg;
    // input_accepted and input_errored
    var input_accepted = this.fieldarg_in_result('set_input_accepted', result, fieldlist);
    var input_errored = this.fieldarg_in_result('set_input_errored', result, fieldlist);
    var self = this;
    var inputindex = 0;
    the_widg.find('input[type="text"]').each(function() {
        // for each text input field, get its index key
        var text_input = $(this);
        if (text_input.prop('disabled')) {
            return true;
            }
        // get the index key of this input field
        var input_key = inputindex.toString();
        inputindex += 1;
        if (input_accepted) {
            if (input_key in input_accepted) {
                self.set_accepted(text_input, input_accepted[input_key]);
                }
            }
        if (input_errored) {
            if (input_key in input_errored) {
                self.set_errored(text_input, input_errored[input_key]);
                }
            }
        })
    };

