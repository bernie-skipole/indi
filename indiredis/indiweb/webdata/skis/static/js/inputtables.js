

SKIPOLE.inputtables = {};


SKIPOLE.inputtables.InputTable1 = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    this.display_errors = false;
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
                if (row_classes[index] !== null) {
                    $(this).attr("class", row_classes[index]);
                    }
                }
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
            if (keysonly && keysonly.length) {
                let rowkey = keysonly[index];
                if (rowkey) {
                    if (keysvals[rowkey] !== null) {
                        // set name attribute and val attribute for each input field
                        let inputtag = $(cells[2]).find('input');
                        inputtag.prop('name', self.formname('inputdict') + "-" + rowkey);
                        inputtag.val(keysvals[rowkey]);
                        }
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



SKIPOLE.inputtables.InputTable4 = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    this.display_errors = false;
    };
SKIPOLE.inputtables.InputTable4.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.inputtables.InputTable4.prototype.constructor = SKIPOLE.inputtables.InputTable4;
SKIPOLE.inputtables.InputTable4.prototype.setvalues = function (fieldlist, result) {
    if (!this.widg_id) {
        return;
        }
    var the_widg = this.widg;
    // columns
    var col1 = this.fieldarg_in_result('col1', result, fieldlist);
    var col2 = this.fieldarg_in_result('col2', result, fieldlist);
    var col3 = this.fieldarg_in_result('col3', result, fieldlist);
    var row_classes = this.fieldarg_in_result('row_classes', result, fieldlist);
    var up_hide = this.fieldarg_in_result('up_hide', result, fieldlist);
    var down_hide = this.fieldarg_in_result('down_hide', result, fieldlist);
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
                if (row_classes[index] !== null) {
                    $(this).attr("class", row_classes[index]);
                    }
                }
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

            let a_link = $(cells[3]).find("a");
            let up_link = $(a_link[0]);
            // up_getfield1
            let up_getfield1 = self.fieldarg_in_result('up_getfield1', result, fieldlist);
            if (up_getfield1 && up_getfield1.length) {
                if (up_getfield1[index] !== null) {
                    let href = up_link.attr('href');
                    let url = self.setgetfield(href, 'up_getfield1',up_getfield1[index]);
                    up_link.attr('href', url);
                    }
                }
            // up_getfield2
            let up_getfield2 = self.fieldarg_in_result('up_getfield2', result, fieldlist);
            if (up_getfield2 && up_getfield2.length) {
                if (up_getfield2[index] !== null) {
                    let href = up_link.attr('href');
                    let url = self.setgetfield(href, 'up_getfield2', up_getfield2[index]);
                    up_link.attr('href', url);
                    }
                }
            // up_hide
            if (up_hide && up_hide.length) {
                if (up_hide[index] !== null) {
                    if (up_hide[index] === true) {
                        up_link.css("visibility", "hidden");
                        }
                    else {
                        up_link.css("visibility", "visible");
                        }
                    }
                }

            let down_link = $(a_link[1]);
            // down_getfield1
            let down_getfield1 = self.fieldarg_in_result('down_getfield1', result, fieldlist);
            if (down_getfield1 && down_getfield1.length) {
                if (down_getfield1[index] !== null) {
                    let href = down_link.attr('href');
                    let url = self.setgetfield(href, 'down_getfield1',down_getfield1[index]);
                    down_link.attr('href', url);
                    }
                }
            // down_getfield2
            let down_getfield2 = self.fieldarg_in_result('down_getfield2', result, fieldlist);
            if (down_getfield2 && down_getfield2.length) {
                if (down_getfield2[index] !== null) {
                    let href = down_link.attr('href');
                    let url = self.setgetfield(href, 'down_getfield2', down_getfield2[index]);
                    down_link.attr('href', url);
                    }
                }
            // down_hide
            if (down_hide && down_hide.length) {
                if (down_hide[index] !== null) {
                    if (down_hide[index] === true) {
                        down_link.css("visibility", "hidden");
                        }
                    else {
                        down_link.css("visibility", "visible");
                        }
                    }
                }

            if (keysonly && keysonly.length) {
                let rowkey = keysonly[index];
                if (rowkey) {
                    // set name attribute and val attribute for each input field
                    if (keysvals[rowkey] !== null) {
                        let inputtag = $(cells[3]).find('input');
                        inputtag.prop('name', self.formname('inputdict') + "-" + rowkey);
                        inputtag.val(keysvals[rowkey]);
                        }
                    }
                 }
             index=index+1;
            }
        })
    };
SKIPOLE.inputtables.InputTable4.prototype.eventfunc = function (e) {
    if (!this.widg_id) {
        return;
        }
    var fieldvalues = this.fieldvalues;
    var the_widg = this.widg;
    var button_pressed = $(e.target);

    if (button_pressed.text() == "\u2191") {
        // up arrow button
        if (!fieldvalues["upurl"]) {
            // no json url, return and call html link
            return;
            }
        var url = fieldvalues["upurl"];
      }
    else if (button_pressed.text() == "\u2193") {
        // down arrow button
        if (!fieldvalues["downurl"]) {
            // no json url, return and call html link
            return;
            }
        var url = fieldvalues["downurl"];
      }
    else {
      // not known
      return;
      }

    var href = button_pressed.attr('href');
    var senddata = href.substring(href.indexOf('?')+1);
    e.preventDefault();
    // respond to json or html
    $.ajax({
          url: url,
          data: senddata
              })
          .done(function(result, textStatus, jqXHR) {
             if (jqXHR.responseJSON) {
                  // JSON response
                  SKIPOLE.setfields(result);
                  } else {
                      // html response
                      document.open();
                      document.write(result);
                      document.close();
                      }
              })
          .fail(function( jqXHR, textStatus, errorThrown ) {
                      if (jqXHR.status == 400 || jqXHR.status == 404 || jqXHR.status == 500)  {
                          document.open();
                          document.write(jqXHR.responseText);
                          document.close();
                          }
                      else {
                          SKIPOLE.json_failed( jqXHR, textStatus, errorThrown );
                          }
              });

    };

