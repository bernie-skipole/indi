

SKIPOLE.confirm = {};

SKIPOLE.confirm.ConfirmBox1 = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    this.display_errors = false;
    };
SKIPOLE.confirm.ConfirmBox1.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.confirm.ConfirmBox1.prototype.constructor = SKIPOLE.confirm.ConfirmBox1;
SKIPOLE.confirm.ConfirmBox1.prototype.setvalues = function (fieldlist, result) {
    if (!this.widg_id) {
        return;
        }
    var the_widg = this.widg;
    // hide
    var hidebox = this.fieldarg_in_result('hide', result, fieldlist);
    if (hidebox != undefined) {
        if (hidebox) {
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
    // para_text
    var paragraph = the_widg.find("p");
    var para_text = this.fieldarg_in_result('para_text', result, fieldlist);
    if (para_text) {
        paragraph.text(para_text);
        }
     var a_1 = the_widg.find("a").first();
     var a_2 = the_widg.find("a").last();
    // get_field1_1
    var get_field1_1 = this.fieldarg_in_result('get_field1_1', result, fieldlist);
    if (get_field1_1 != undefined) {
        var href = a_1.attr('href');
        var url = this.setgetfield(href, "get_field1_1", get_field1_1);
        a_1.attr('href', url);
        }
    // get_field1_2
    var get_field1_2 = this.fieldarg_in_result('get_field1_2', result, fieldlist);
    if (get_field1_2 != undefined) {
        var href = a_1.attr('href');
        var url = this.setgetfield(href, "get_field1_2", get_field1_2);
        a_1.attr('href', url);
        }
    // get_field1_3
    var get_field1_3 = this.fieldarg_in_result('get_field1_3', result, fieldlist);
    if (get_field1_3 != undefined) {
        var href = a_1.attr('href');
        var url = this.setgetfield(href, "get_field1_3", get_field1_3);
        a_1.attr('href', url);
        }
    // get_field2_1
    var get_field2_1 = this.fieldarg_in_result('get_field2_1', result, fieldlist);
    if (get_field2_1 != undefined) {
        var href = a_2.attr('href');
        var url = this.setgetfield(href, "get_field2_1", get_field2_1);
        a_2.attr('href', url);
        }
    // get_field2_2
    var get_field2_2 = this.fieldarg_in_result('get_field2_2', result, fieldlist);
    if (get_field2_2 != undefined) {
        var href = a_2.attr('href');
        var url = this.setgetfield(href, "get_field2_2", get_field2_2);
        a_2.attr('href', url);
        }
    // get_field2_3
    var get_field2_3 = this.fieldarg_in_result('get_field2_3', result, fieldlist);
    if (get_field2_3 != undefined) {
        var href = a_2.attr('href');
        var url = this.setgetfield(href, "get_field2_3", get_field2_3);
        a_2.attr('href', url);
        }
    };
SKIPOLE.confirm.ConfirmBox1.prototype.eventfunc = function (e) {
    SKIPOLE.skiprefresh = true;
    if (!this.widg_id) {
        return;
        }
    var fieldvalues = this.fieldvalues;
    var button = $(e.target);
    var button_num = button.index();
    var href = button.attr('href');
    if (!href) {
        return;
        }
    var senddata = href.substring(href.indexOf('?')+1);
    if (button_num === 0) {
        if (!fieldvalues["url1"]) {
            return;
            }
        e.preventDefault();
        // respond to json or html
        $.ajax({
              url: fieldvalues["url1"],
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
        } else if (button_num === 1) {
            if (!fieldvalues["url2"]) {
                return;
                }
            e.preventDefault();
            // respond to json or html
            $.ajax({
                  url: fieldvalues["url2"],
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
        }
    };


SKIPOLE.confirm.ConfirmBox2 = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    this.display_errors = false;
    };
SKIPOLE.confirm.ConfirmBox2.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.confirm.ConfirmBox2.prototype.constructor = SKIPOLE.confirm.ConfirmBox2;
SKIPOLE.confirm.ConfirmBox2.prototype.setvalues = function (fieldlist, result) {
    if (!this.widg_id) {
        return;
        }
    var the_widg = this.widg;
    // hide
    var hidebox = this.fieldarg_in_result('hide', result, fieldlist);
    if (hidebox != undefined) {
        if (hidebox) {
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
    // para_text
    var paragraph = the_widg.find("p");
    var para_text = this.fieldarg_in_result('para_text', result, fieldlist);
    if (para_text) {
        paragraph.text(para_text);
        }
     var a_1 = the_widg.find("a").first();
     var a_2 = the_widg.find("a").last();
    // get_field1_1
    var get_field1_1 = this.fieldarg_in_result('get_field1_1', result, fieldlist);
    if (get_field1_1 != undefined) {
        var href = a_1.attr('href');
        var url = this.setgetfield(href, "get_field1_1", get_field1_1);
        a_1.attr('href', url);
        }
    // get_field1_2
    var get_field1_2 = this.fieldarg_in_result('get_field1_2', result, fieldlist);
    if (get_field1_2 != undefined) {
        var href = a_1.attr('href');
        var url = this.setgetfield(href, "get_field1_2", get_field1_2);
        a_1.attr('href', url);
        }
    // get_field1_3
    var get_field1_3 = this.fieldarg_in_result('get_field1_3', result, fieldlist);
    if (get_field1_3 != undefined) {
        var href = a_1.attr('href');
        var url = this.setgetfield(href, "get_field1_3", get_field1_3);
        a_1.attr('href', url);
        }
    // get_field2_1
    var get_field2_1 = this.fieldarg_in_result('get_field2_1', result, fieldlist);
    if (get_field2_1 != undefined) {
        var href = a_2.attr('href');
        var url = this.setgetfield(href, "get_field2_1", get_field2_1);
        a_2.attr('href', url);
        }
    // get_field2_2
    var get_field2_2 = this.fieldarg_in_result('get_field2_2', result, fieldlist);
    if (get_field2_2 != undefined) {
        var href = a_2.attr('href');
        var url = this.setgetfield(href, "get_field2_2", get_field2_2);
        a_2.attr('href', url);
        }
    // get_field2_3
    var get_field2_3 = this.fieldarg_in_result('get_field2_3', result, fieldlist);
    if (get_field2_3 != undefined) {
        var href = a_2.attr('href');
        var url = this.setgetfield(href, "get_field2_3", get_field2_3);
        a_2.attr('href', url);
        }
    };
SKIPOLE.confirm.ConfirmBox2.prototype.eventfunc = function (e) {
    SKIPOLE.skiprefresh = true;
    if (!this.widg_id) {
        return;
        }
    if ( $(e.target).index() === 0 ) {
        this.widg.fadeOut('slow');
        e.preventDefault();
        }
     };



SKIPOLE.confirm.AlertClear1 = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    };
SKIPOLE.confirm.AlertClear1.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.confirm.AlertClear1.prototype.constructor = SKIPOLE.confirm.AlertClear1;
SKIPOLE.confirm.AlertClear1.prototype.setvalues = function (fieldlist, result) {
    if (!this.widg_id) {
        return;
        }
    /* check if an error message or clear_error is given */
    var is_error = this.check_error(fieldlist, result);
    var the_widg = this.widg;
    if (!is_error) {
        // if no error condition check hide and para_text
        var para_text = this.fieldarg_in_result('para_text', result, fieldlist);
        if (para_text != undefined) {
            var paragraph = the_widg.find("p:last");
            paragraph.text(para_text);
            }
        var hidebox = this.fieldarg_in_result('hide', result, fieldlist);
        if (hidebox != undefined) {
            if (hidebox) {
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
        }
    var button = the_widg.find("a");
    // get_field1
    var get_field1 = this.fieldarg_in_result('get_field1', result, fieldlist);
    if (get_field1 != undefined) {
        var href = button.attr('href');
        var url = this.setgetfield(href, "get_field1", get_field1);
        button.attr('href', url);
        }
    // get_field2
    var get_field2 = this.fieldarg_in_result('get_field2', result, fieldlist);
    if (get_field2 != undefined) {
        var href = button.attr('href');
        var url = this.setgetfield(href, "get_field2", get_field2);
        button.attr('href', url);
        }
    // get_field3
    var get_field3 = this.fieldarg_in_result('get_field3', result, fieldlist);
    if (get_field3 != undefined) {
        var href = button.attr('href');
        var url = this.setgetfield(href, "get_field3", get_field3);
        button.attr('href', url);
        }
    };
SKIPOLE.confirm.AlertClear1.prototype.eventfunc = function (e) {
    // pressing close is the equivalent of clearing the error
    // and preventing the link send
    SKIPOLE.skiprefresh = true;
    this.clear_error();
    e.preventDefault();
    };
SKIPOLE.confirm.AlertClear1.prototype.show_error = function (error_message) {
    if (!this.widg_id) {
        return;
        }
    if (!error_message) {
        error_message = this.error_message;
        }
    if (!error_message) {
        error_message = "Unknown Error";
        }
    var the_widg = this.widg;
    the_widg.attr("data-status", "error");
    var fieldvalues = this.fieldvalues;
    // get error_class to insert into div with inner_id
    if (fieldvalues["inner_id"]) {
        var inner_div = $('#' + fieldvalues["inner_id"]);
        if (fieldvalues["inner_class"]) {
            inner_div.removeClass(fieldvalues["inner_class"]);
            }
        if (fieldvalues["error_class"]) {
            inner_div.addClass(fieldvalues["error_class"]);
            }
        }
    // get error para to insert error message
    var paragraph = the_widg.find("p:last");
    paragraph.text(error_message);
    if (!(the_widg.is(":visible"))) {
        the_widg.fadeIn('slow');
        }
    };
SKIPOLE.confirm.AlertClear1.prototype.clear_error = function() {
    if (!this.widg_id) {
        return;
        }
    var the_widg = this.widg;
    if (the_widg.attr("data-status") == "error") {
        the_widg.removeAttr( "data-status" )
        }
    if (the_widg.is(":visible")) {
        the_widg.fadeOut('slow');
        }
    var fieldvalues = this.fieldvalues;
    if (!fieldvalues["inner_id"]) {
        return;
        }
    var inner_div = $('#' + fieldvalues["inner_id"]);
    if (fieldvalues["error_class"]) {
        inner_div.removeClass(fieldvalues["error_class"]);
        }
    if (fieldvalues["inner_class"]) {
        inner_div.addClass(fieldvalues["inner_class"]);
        }
    };



SKIPOLE.confirm.AlertClear2 = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    };
SKIPOLE.confirm.AlertClear2.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.confirm.AlertClear2.prototype.constructor = SKIPOLE.confirm.AlertClear2;
SKIPOLE.confirm.AlertClear2.prototype.setvalues = function (fieldlist, result) {
    if (!this.widg_id) {
        return;
        }
    /* check if an error message or clear_error is given */
    var is_error = this.check_error(fieldlist, result);
    var the_widg = this.widg;
    if (!is_error) {
        // if no error condition check hide and para_text
        var para_text = this.fieldarg_in_result('para_text', result, fieldlist);
        if (para_text != undefined) {
            var paragraph = the_widg.find("p:last");
            paragraph.text(para_text);
            }
        var hidebox = this.fieldarg_in_result('hide', result, fieldlist);
        if (hidebox != undefined) {
            if (hidebox) {
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
        }
    var button = the_widg.find("a");
    // get_field1
    var get_field1 = this.fieldarg_in_result('get_field1', result, fieldlist);
    if (get_field1 != undefined) {
        var href = button.attr('href');
        var url = this.setgetfield(href, "get_field1", get_field1);
        button.attr('href', url);
        }
    // get_field2
    var get_field2 = this.fieldarg_in_result('get_field2', result, fieldlist);
    if (get_field2 != undefined) {
        var href = button.attr('href');
        var url = this.setgetfield(href, "get_field2", get_field2);
        button.attr('href', url);
        }
    // get_field3
    var get_field3 = this.fieldarg_in_result('get_field3', result, fieldlist);
    if (get_field3 != undefined) {
        var href = button.attr('href');
        var url = this.setgetfield(href, "get_field3", get_field3);
        button.attr('href', url);
        }
    };
SKIPOLE.confirm.AlertClear2.prototype.eventfunc = function (e) {
    // pressing close is the equivalent of clearing the error
    // and calling for json or html page
    SKIPOLE.skiprefresh = true;
    this.clear_error();
    if (!this.widg_id) {
        return;
        }
    var button = this.widg.find("a");
    var fieldvalues = this.fieldvalues;
    if (!fieldvalues["url"]) {
        // no json url, return and call html link
        return;
        }
    var href = button.attr('href');
    var senddata = href.substring(href.indexOf('?')+1);
    e.preventDefault();
    // respond to json or html
    $.ajax({
          url: fieldvalues["url"],
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
SKIPOLE.confirm.AlertClear2.prototype.show_error = function (error_message) {
    if (!this.widg_id) {
        return;
        }
    if (!error_message) {
        error_message = this.error_message;
        }
    if (!error_message) {
        error_message = "Unknown Error";
        }
    var the_widg = this.widg;
    the_widg.attr("data-status", "error");
    var fieldvalues = this.fieldvalues;
    // get error_class to insert into div with inner_id
    if (fieldvalues["inner_id"]) {
        var inner_div = $('#' + fieldvalues["inner_id"]);
        if (fieldvalues["inner_class"]) {
            inner_div.removeClass(fieldvalues["inner_class"]);
            }
        if (fieldvalues["error_class"]) {
            inner_div.addClass(fieldvalues["error_class"]);
            }
        }
    // get error para to insert error message
    var paragraph = the_widg.find("p:last");
    paragraph.text(error_message);
    if (!(the_widg.is(":visible"))) {
        the_widg.fadeIn('slow');
        }
    };
SKIPOLE.confirm.AlertClear2.prototype.clear_error = function() {
    if (!this.widg_id) {
        return;
        }
    var the_widg = this.widg;
    if (the_widg.attr("data-status") == "error") {
        the_widg.removeAttr( "data-status" )
        }
    if (the_widg.is(":visible")) {
        the_widg.fadeOut('slow');
        }
    var fieldvalues = this.fieldvalues;
    if (!fieldvalues["inner_id"]) {
        return;
        }
    var inner_div = $('#' + fieldvalues["inner_id"]);
    if (fieldvalues["error_class"]) {
        inner_div.removeClass(fieldvalues["error_class"]);
        }
    if (fieldvalues["inner_class"]) {
        inner_div.addClass(fieldvalues["inner_class"]);
        }
    };


