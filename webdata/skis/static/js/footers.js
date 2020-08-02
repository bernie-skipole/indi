
SKIPOLE.footers = {};

SKIPOLE.footers.SimpleFooter = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    };
SKIPOLE.footers.SimpleFooter.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.footers.SimpleFooter.prototype.constructor = SKIPOLE.footers.SimpleFooter;
SKIPOLE.footers.SimpleFooter.prototype.setvalues = function (fieldlist, result) {
    if (!this.widg_id) {
        return;
        }
    /* check if an error message or clear_error is given */
    this.check_error(fieldlist, result);
    var the_widg = this.widg;
    // footer_text
    var footer_text = this.fieldarg_in_result('footer_text', result, fieldlist);
    if (footer_text) {
	    var textident = this.fieldvalues["textident"];
	    if (!textident) {
	        return;
            }
	    $('#'+textident).text(footer_text);
        }
    };




