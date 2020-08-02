

SKIPOLE.inputtables = {};


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

