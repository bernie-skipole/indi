
SKIPOLE.tables = {};

SKIPOLE.tables.ColorTable1 = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    this.display_errors = false;
    };
SKIPOLE.tables.ColorTable1.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.tables.ColorTable1.prototype.constructor = SKIPOLE.tables.ColorTable1;


SKIPOLE.tables.TwoColTable1 = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    this.display_errors = false;
    };
SKIPOLE.tables.TwoColTable1.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.tables.TwoColTable1.prototype.constructor = SKIPOLE.tables.TwoColTable1;
SKIPOLE.tables.TwoColTable1.prototype.setvalues = function (fieldlist, result) {
    if (!this.widg_id) {
        return;
        }
    var the_widg = this.widg;
    // col1 and col2
    var col1 = this.fieldarg_in_result('col1', result, fieldlist);
    var col2 = this.fieldarg_in_result('col2', result, fieldlist);
    var self = this;
    var index = 0;
    var header = false;
    if (the_widg.find('th').length) {
        header = true;
        }
    the_widg.find('tr').each(function() {
        if (header) {
            header = false;
            }
        else {
            // for each row
            var cells = $(this).children();
            if (col1 && col1.length) {
                if (col1[index] !== null) {
                    $(cells[0]).text(col1[index]);
                    }
                 }
            if (col2 && col2.length) {
                if (col2[index] !== null) {
                    $(cells[1]).text(col2[index]);
                    }
                }
             index=index+1;
            }
        })
    };


SKIPOLE.tables.ThreeColTable1 = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    this.display_errors = false;
    };
SKIPOLE.tables.ThreeColTable1.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.tables.ThreeColTable1.prototype.constructor = SKIPOLE.tables.ThreeColTable1;
SKIPOLE.tables.ThreeColTable1.prototype.setvalues = function (fieldlist, result) {
    if (!this.widg_id) {
        return;
        }
    var the_widg = this.widg;
    // columns
    var col1 = this.fieldarg_in_result('col1', result, fieldlist);
    var col2 = this.fieldarg_in_result('col2', result, fieldlist);
    var col3 = this.fieldarg_in_result('col3', result, fieldlist);
    var self = this;
    var index = 0;
    var header = false;
    if (the_widg.find('th').length) {
        header = true;
        }
    the_widg.find('tr').each(function() {
        if (header) {
            header = false;
            }
        else {
            // for each row
            var cells = $(this).children();
            if (col1 && col1.length) {
                if (col1[index] !== null) {
                    $(cells[0]).text(col1[index]);
                    }
                 }
            if (col2 && col2.length) {
                if (col2[index] !== null) {
                    $(cells[1]).text(col2[index]);
                    }
                }
            if (col3 && col3.length) {
                if (col3[index] !== null) {
                    $(cells[2]).text(col3[index]);
                    }
                }
             index=index+1;
            }
        })
    };


SKIPOLE.tables.TextBlockTable2 = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    this.display_errors = false;
    };
SKIPOLE.tables.TextBlockTable2.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.tables.TextBlockTable2.prototype.constructor = SKIPOLE.tables.TextBlockTable2;


SKIPOLE.tables.ButtonTextBlockTable1 = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    };
SKIPOLE.tables.ButtonTextBlockTable1.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.tables.ButtonTextBlockTable1.prototype.constructor = SKIPOLE.tables.ButtonTextBlockTable1;
SKIPOLE.tables.ButtonTextBlockTable1.prototype.setvalues = function (fieldlist, result) {
    if (!this.widg_id) {
        return;
        }
    // sets hidden fields
    this.sethiddenfields(fieldlist, result);
    };




