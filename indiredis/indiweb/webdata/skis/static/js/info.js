
SKIPOLE.info = {};

SKIPOLE.info.ServerTimeStamp = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    this.display_errors = false;
    };
SKIPOLE.info.ServerTimeStamp.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.info.ServerTimeStamp.prototype.constructor = SKIPOLE.info.ServerTimeStamp;
SKIPOLE.info.ServerTimeStamp.prototype.setvalues = function (fieldlist, result) {
    if (!this.widg_id) {
        return;
        }
    var timestamp_text = this.fieldarg_in_result('timestamp', result, fieldlist);
    if (timestamp_text) {
        this.widg.text(timestamp_text);
        }
    };


SKIPOLE.info.PageIdent = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    this.display_errors = false;
    };
SKIPOLE.info.PageIdent.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.info.PageIdent.prototype.constructor = SKIPOLE.info.PageIdent;
SKIPOLE.info.PageIdent.prototype.setvalues = function (fieldlist, result) {
    /* This widget accepts fields - span_text */
   if (!this.widg_id) {
        return;
        }
    var span_text = this.fieldarg_in_result('span_text', result, fieldlist);
    if (span_text) {
        this.widg.text(span_text);
        }
    };


SKIPOLE.info.PageName = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    this.display_errors = false;
    };
SKIPOLE.info.PageName.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.info.PageName.prototype.constructor = SKIPOLE.info.PageName;
SKIPOLE.info.PageName.prototype.setvalues = function (fieldlist, result) {
    /* This widget accepts fields - span_text */
   if (!this.widg_id) {
        return;
        }
    var span_text = this.fieldarg_in_result('span_text', result, fieldlist);
    if (span_text) {
        this.widg.text(span_text);
        }
    };


SKIPOLE.info.PageDescription = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    this.display_errors = false;
    };
SKIPOLE.info.PageDescription.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.info.PageDescription.prototype.constructor = SKIPOLE.info.PageDescription;
SKIPOLE.info.PageDescription.prototype.setvalues = function (fieldlist, result) {
    /* This widget accepts fields - span_text */
   if (!this.widg_id) {
        return;
        }
    var span_text = this.fieldarg_in_result('span_text', result, fieldlist);
    if (span_text) {
        this.widg.text(span_text);
        }
    };


SKIPOLE.info.Redirector = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    this.display_errors = false;
    };
SKIPOLE.info.Redirector.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.info.Redirector.prototype.constructor = SKIPOLE.info.Redirector;


SKIPOLE.info.ProjectName = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    this.display_errors = false;
    };
SKIPOLE.info.ProjectName.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.info.ProjectName.prototype.constructor = SKIPOLE.info.ProjectName;


SKIPOLE.info.Version = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    this.display_errors = false;
    };
SKIPOLE.info.Version.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.info.Version.prototype.constructor = SKIPOLE.info.Version;


SKIPOLE.info.SkipoleVersion = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    this.display_errors = false;
    };
SKIPOLE.info.SkipoleVersion.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.info.SkipoleVersion.prototype.constructor = SKIPOLE.info.SkipoleVersion;


SKIPOLE.info.ProgressBar1 = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    this.display_errors = false;
    };
SKIPOLE.info.ProgressBar1.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.info.ProgressBar1.prototype.constructor = SKIPOLE.info.ProgressBar1;
SKIPOLE.info.ProgressBar1.prototype.setvalues = function (fieldlist, result) {
    if (!this.widg_id) {
        return;
        }
    var progress = $("#" + this.fieldvalues["progressident"]);
    var valuetext = this.fieldarg_in_result('text', result, fieldlist);
    if (valuetext) {
        progress.text(valuetext);
        }
    var value = this.fieldarg_in_result('value', result, fieldlist);
    if (value || value === 0) {
        progress.attr("value", value);
        }
    };





