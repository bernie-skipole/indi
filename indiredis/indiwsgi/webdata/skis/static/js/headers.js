

SKIPOLE.headers = {};


SKIPOLE.headers.HeaderErrorPara = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    };
SKIPOLE.headers.HeaderErrorPara.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.headers.HeaderErrorPara.prototype.constructor = SKIPOLE.headers.HeaderErrorPara;
SKIPOLE.headers.HeaderErrorPara.prototype.setvalues = function (fieldlist, result) {
    /* accept show_error */
    if (!this.widg_id) {
        return;
        }
    /* check if an error message or clear_error is given */
    this.check_error(fieldlist, result);
    /*  if hide is given */
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
    };
SKIPOLE.headers.HeaderErrorPara.prototype.show_error = function (error_message) {
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
    if (!(the_widg.is(":visible"))) {
        the_widg.text(error_message).fadeIn('slow');
        }
    };
SKIPOLE.headers.HeaderErrorPara.prototype.clear_error = function() {
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
    };


SKIPOLE.headers.HeadText = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    this.display_errors = false;
    };
SKIPOLE.headers.HeadText.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.headers.HeadText.prototype.constructor = SKIPOLE.headers.HeadText;
SKIPOLE.headers.HeadText.prototype.setvalues = function (fieldlist, result) {
    /* This widget accepts field - large_text */
   if (!this.widg_id) {
        return;
        }
    var the_widg = this.widg;
    /* large_text */
    var large_text = this.fieldarg_in_result('large_text', result, fieldlist);
    if (large_text) {
        the_widg.text(large_text);
        }
    };



SKIPOLE.headers.HeaderText1 = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    };
SKIPOLE.headers.HeaderText1.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.headers.HeaderText1.prototype.constructor = SKIPOLE.headers.HeaderText1;
SKIPOLE.headers.HeaderText1.prototype.setvalues = function (fieldlist, result) {
    if (!this.widg_id) {
        return;
        }
    /* check if an error message or clear_error is given */
    this.check_error(fieldlist, result);
    var the_widg = this.widg;
    // large_text
    var large_text = this.fieldarg_in_result('large_text', result, fieldlist);
    if (large_text) {
        var h1_text = the_widg.find('h1');
        h1_text.text(large_text);
        }
    // small_text
    var small_text = this.fieldarg_in_result('small_text', result, fieldlist);
    if (small_text) {
        var p_text = the_widg.find(':nth-child(2)');
        p_text.text(small_text);
        }
    };
SKIPOLE.headers.HeaderText1.prototype.show_error = function (error_message) {
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

    var error_div = the_widg.find(':nth-child(3)');
    var error_para = error_div.find(':first');
    error_para.text(error_message);
    if (!(error_div.is(":visible"))) {
       error_div.show();
        }
    };
SKIPOLE.headers.HeaderText1.prototype.clear_error = function () {
    if (!this.widg_id) {
        return;
        }
    var the_widg = this.widg;
    the_widg.removeAttr("data-status");
    var error_div = the_widg.find(':nth-child(3)');
    if (error_div.is(":visible")) {
        //error_div.fadeOut('slow');
        error_div.hide();
        }
    };


SKIPOLE.headers.HeaderText2 = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    };
SKIPOLE.headers.HeaderText2.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.headers.HeaderText2.prototype.constructor = SKIPOLE.headers.HeaderText2;
SKIPOLE.headers.HeaderText2.prototype.setvalues = function (fieldlist, result) {
    if (!this.widg_id) {
        return;
        }
    /* check if an error message or clear_error is given */
    this.check_error(fieldlist, result);
    var the_widg = this.widg;
    // large_text
    var large_text = this.fieldarg_in_result('large_text', result, fieldlist);
    if (large_text) {
        var h1_text = the_widg.find('h2');
        h1_text.text(large_text);
        }
    // small_text
    var small_text = this.fieldarg_in_result('small_text', result, fieldlist);
    if (small_text) {
        var p_text = the_widg.find(':nth-child(2)');
        p_text.text(small_text);
        }
    };
SKIPOLE.headers.HeaderText2.prototype.show_error = function (error_message) {
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

    var error_div = the_widg.find(':nth-child(3)');
    var error_para = error_div.find(':first');
    error_para.text(error_message);
    if (!(error_div.is(":visible"))) {
       error_div.show();
        }
    };
SKIPOLE.headers.HeaderText2.prototype.clear_error = function () {
    if (!this.widg_id) {
        return;
        }
    var the_widg = this.widg;
    the_widg.removeAttr("data-status");
    var error_div = the_widg.find(':nth-child(3)');
    if (error_div.is(":visible")) {
        //error_div.fadeOut('slow');
        error_div.hide();
        }
    };


SKIPOLE.headers.HeaderText3 = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    };
SKIPOLE.headers.HeaderText3.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.headers.HeaderText3.prototype.constructor = SKIPOLE.headers.HeaderText3;
SKIPOLE.headers.HeaderText3.prototype.setvalues = function (fieldlist, result) {
    if (!this.widg_id) {
        return;
        }
    /* check if an error message or clear_error is given */
    this.check_error(fieldlist, result);
    var the_widg = this.widg;
    // large_text
    var large_text = this.fieldarg_in_result('large_text', result, fieldlist);
    if (large_text) {
        var h1_text = the_widg.find('h3');
        h1_text.text(large_text);
        }
    // small_text
    var small_text = this.fieldarg_in_result('small_text', result, fieldlist);
    if (small_text) {
        var p_text = the_widg.find(':nth-child(2)');
        p_text.text(small_text);
        }
    };
SKIPOLE.headers.HeaderText3.prototype.show_error = function (error_message) {
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

    var error_div = the_widg.find(':nth-child(3)');
    var error_para = error_div.find(':first');
    error_para.text(error_message);
    if (!(error_div.is(":visible"))) {
       error_div.show();
        }
    };
SKIPOLE.headers.HeaderText3.prototype.clear_error = function () {
    if (!this.widg_id) {
        return;
        }
    var the_widg = this.widg;
    the_widg.removeAttr("data-status");
    var error_div = the_widg.find(':nth-child(3)');
    if (error_div.is(":visible")) {
        //error_div.fadeOut('slow');
        error_div.hide();
        }
    };


SKIPOLE.headers.HeaderText4 = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    };
SKIPOLE.headers.HeaderText4.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.headers.HeaderText4.prototype.constructor = SKIPOLE.headers.HeaderText4;
SKIPOLE.headers.HeaderText4.prototype.setvalues = function (fieldlist, result) {
    if (!this.widg_id) {
        return;
        }
    /* check if an error message or clear_error is given */
    this.check_error(fieldlist, result);
    var the_widg = this.widg;
    // large_text
    var large_text = this.fieldarg_in_result('large_text', result, fieldlist);
    if (large_text) {
        var h1_text = the_widg.find('h4');
        h1_text.text(large_text);
        }
    // small_text
    var small_text = this.fieldarg_in_result('small_text', result, fieldlist);
    if (small_text) {
        var p_text = the_widg.find(':nth-child(2)');
        p_text.text(small_text);
        }
    };
SKIPOLE.headers.HeaderText4.prototype.show_error = function (error_message) {
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

    var error_div = the_widg.find(':nth-child(3)');
    var error_para = error_div.find(':first');
    error_para.text(error_message);
    if (!(error_div.is(":visible"))) {
       error_div.show();
        }
    };
SKIPOLE.headers.HeaderText4.prototype.clear_error = function () {
    if (!this.widg_id) {
        return;
        }
    var the_widg = this.widg;
    the_widg.removeAttr("data-status");
    var error_div = the_widg.find(':nth-child(3)');
    if (error_div.is(":visible")) {
        //error_div.fadeOut('slow');
        error_div.hide();
        }
    };

SKIPOLE.headers.HeaderText5 = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    };
SKIPOLE.headers.HeaderText5.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.headers.HeaderText5.prototype.constructor = SKIPOLE.headers.HeaderText5;
SKIPOLE.headers.HeaderText5.prototype.setvalues = function (fieldlist, result) {
    if (!this.widg_id) {
        return;
        }
    /* check if an error message or clear_error is given */
    this.check_error(fieldlist, result);
    var the_widg = this.widg;
    // large_text
    var large_text = this.fieldarg_in_result('large_text', result, fieldlist);
    if (large_text) {
        var h1_text = the_widg.find('h5');
        h1_text.text(large_text);
        }
    // small_text
    var small_text = this.fieldarg_in_result('small_text', result, fieldlist);
    if (small_text) {
        var p_text = the_widg.find(':nth-child(2)');
        p_text.text(small_text);
        }
    };
SKIPOLE.headers.HeaderText5.prototype.show_error = function (error_message) {
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

    var error_div = the_widg.find(':nth-child(3)');
    var error_para = error_div.find(':first');
    error_para.text(error_message);
    if (!(error_div.is(":visible"))) {
       error_div.show();
        }
    };
SKIPOLE.headers.HeaderText5.prototype.clear_error = function () {
    if (!this.widg_id) {
        return;
        }
    var the_widg = this.widg;
    the_widg.removeAttr("data-status");
    var error_div = the_widg.find(':nth-child(3)');
    if (error_div.is(":visible")) {
        //error_div.fadeOut('slow');
        error_div.hide();
        }
    };


SKIPOLE.headers.HeaderText6 = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    };
SKIPOLE.headers.HeaderText6.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.headers.HeaderText6.prototype.constructor = SKIPOLE.headers.HeaderText6;
SKIPOLE.headers.HeaderText6.prototype.setvalues = function (fieldlist, result) {
    if (!this.widg_id) {
        return;
        }
    /* check if an error message or clear_error is given */
    this.check_error(fieldlist, result);
    var the_widg = this.widg;
    // large_text
    var large_text = this.fieldarg_in_result('large_text', result, fieldlist);
    if (large_text) {
        var h1_text = the_widg.find('h6');
        h1_text.text(large_text);
        }
    // small_text
    var small_text = this.fieldarg_in_result('small_text', result, fieldlist);
    if (small_text) {
        var p_text = the_widg.find(':nth-child(2)');
        p_text.text(small_text);
        }
    };
SKIPOLE.headers.HeaderText6.prototype.show_error = function (error_message) {
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

    var error_div = the_widg.find(':nth-child(3)');
    var error_para = error_div.find(':first');
    error_para.text(error_message);
    if (!(error_div.is(":visible"))) {
       error_div.show();
        }
    };
SKIPOLE.headers.HeaderText6.prototype.clear_error = function () {
    if (!this.widg_id) {
        return;
        }
    var the_widg = this.widg;
    the_widg.removeAttr("data-status");
    var error_div = the_widg.find(':nth-child(3)');
    if (error_div.is(":visible")) {
        //error_div.fadeOut('slow');
        error_div.hide();
        }
    };

SKIPOLE.headers.NavButtons1 = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    };
SKIPOLE.headers.NavButtons1.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.headers.NavButtons1.prototype.constructor = SKIPOLE.headers.NavButtons1;


SKIPOLE.headers.NavButtons2 = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    this.display_errors = false;
    };
SKIPOLE.headers.NavButtons2.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.headers.NavButtons2.prototype.constructor = SKIPOLE.headers.NavButtons2;


SKIPOLE.headers.NavButtons3 = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    this.display_errors = false;
    };
SKIPOLE.headers.NavButtons3.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.headers.NavButtons3.prototype.constructor = SKIPOLE.headers.NavButtons3;
SKIPOLE.headers.NavButtons3.prototype.setvalues = function (fieldlist, result) {
    if (!this.widg_id) {
        return;
        }
    var the_widg = this.widg;
    // links
    var button_text = this.fieldarg_in_result('button_text', result, fieldlist);
    var get_field1 = this.fieldarg_in_result('get_field1', result, fieldlist);
    var get_field2 = this.fieldarg_in_result('get_field2', result, fieldlist);
    var button_classes = this.fieldarg_in_result('button_classes', result, fieldlist);

    var self = this;
    var index = 0;

    the_widg.find('a').each(function() {
            // for each link
            // set its class
            if (button_classes && button_classes.length) {
                if (button_classes[index] !== null) {
                    $(this).attr("class", button_classes[index]);
                    }
                }
            if (button_text && button_text.length) {
                if (button_text[index] !== null) {
                    $(this).text(button_text[index]);
                    }
                }
            /* get_field1 */
            if (get_field1 && get_field1.length) {
                if (get_field1[index] !== null) {
                    let href = $(this).attr('href');
                    let url = self.setgetfield(href, 'get_field1',get_field1[index]);
                    $(this).attr('href', url);
                    }
                }
            /* get_field2 */
            if (get_field2 && get_field2.length) {
                if (get_field2[index] !== null) {
                    let href = $(this).attr('href');
                    let url = self.setgetfield(href, 'get_field2',get_field2[index]);
                    $(this).attr('href', url);
                    }
                }
             index=index+1;
        })
    };

SKIPOLE.headers.NavButtons3.prototype.eventfunc = function (e) {
    if (!this.widg_id) {
        return;
        }
    var fieldvalues = this.fieldvalues;
    if (!fieldvalues["jsonurl"]) {
        // no json url, return and call html link
        return;
        }

    var the_widg = this.widg;
    var button_pressed = $(e.target);
    var url = fieldvalues["jsonurl"];

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


SKIPOLE.headers.TabButtons1 = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    this.display_errors = false;
    };
SKIPOLE.headers.TabButtons1.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.headers.TabButtons1.prototype.constructor = SKIPOLE.headers.TabButtons1;
SKIPOLE.headers.TabButtons1.prototype.eventfunc = function (e) {
    var button = $(e.target);
    this.setbutton(button.index());
    }
SKIPOLE.headers.TabButtons1.prototype.setbutton = function (button_index) {
    if (!this.widg_id) {
        return;
        }
    var fieldvalues = this.fieldvalues;
    var allbuttons = this.widg.find('button');
    // hide all items with hide_class
    if (fieldvalues["hide_class"]) {
        $("." + fieldvalues["hide_class"]).hide();
        }
    var number_of_buttons = allbuttons.length;
    // handle situation where button_index does not match a button
    if ((button_index < 0) || (button_index >= number_of_buttons)) {
        if (fieldvalues["onclick_removeclass"]){
            // add the class to all buttons (to be removed when a button is pressed)
            allbuttons.addClass( fieldvalues["onclick_removeclass"] );
            }
        if (fieldvalues["onclick_addclass"]){
            // remove the class from all buttons (to be added when a button is pressed)
            allbuttons.removeClass( fieldvalues["onclick_addclass"] );
            }
        return;
        }
    // button_index is valid, get the button
    var button = allbuttons.eq(button_index);
    if (fieldvalues["onclick_removeclass"]){
        // add the class to all buttons (to be removed from the pressed button)
        allbuttons.addClass( fieldvalues["onclick_removeclass"] );
        // remove this class from the pressed button
        button.removeClass( fieldvalues["onclick_removeclass"] );
        }
    if (fieldvalues["onclick_addclass"]){
        // remove the class from all buttons (to be added to the pressed button)
        allbuttons.removeClass( fieldvalues["onclick_addclass"] );
        // add this class to the pressed button
        button.addClass( fieldvalues["onclick_addclass"] );
        }
    // display the item with the given id
    var displayid = fieldvalues["display_id_list"][button_index];
    if (displayid) {
        $("#" + displayid).show();
        }
    }
SKIPOLE.headers.TabButtons1.prototype.setvalues = function (fieldlist, result) {
    // activate a button
    var active_button = this.fieldarg_in_result('active_button', result, fieldlist);
    if (active_button != undefined) {
        this.setbutton(active_button);
        }
    }


SKIPOLE.headers.DropDownButton1 = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    this.display_errors = false;
    };
SKIPOLE.headers.DropDownButton1.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.headers.DropDownButton1.prototype.constructor = SKIPOLE.headers.DropDownButton1;



