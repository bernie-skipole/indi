

SKIPOLE.upload = {};


SKIPOLE.upload.SubmitUploadFile1 = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    };
SKIPOLE.upload.SubmitUploadFile1.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.upload.SubmitUploadFile1.prototype.constructor = SKIPOLE.upload.SubmitUploadFile1;
SKIPOLE.upload.SubmitUploadFile1.prototype.setvalues = function (fieldlist, result) {
    /* This widget accepts fields - hide */
    if (!this.widg_id) {
        return;
        }
    var the_widg = this.widg;

    /* check if an error message or clear_error is given */
    if (this.check_error(fieldlist, result)) {
        return;
        }
    // sets hidden fields
    this.sethiddenfields(fieldlist, result);
    // set hide
    var set_hide = this.fieldarg_in_result('hide', result, fieldlist);
    if (set_hide !== undefined) {
        if (set_hide) {
            if (the_widg.is(":visible")) {
                the_widg.fadeOut('slow');
                }
            }
        else {
            if (!(the_widg.is(":visible"))) {
                the_widg.fadeIn('slow');
                 }
            }
        }
    };


SKIPOLE.upload.UploadFile1 = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    this.display_errors = false;
    };
SKIPOLE.upload.UploadFile1.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.upload.UploadFile1.prototype.constructor = SKIPOLE.upload.UploadFile1;

