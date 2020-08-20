
SKIPOLE.inputtext = {};


SKIPOLE.inputtext.TextInput1 = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    this.display_errors = false;
    };
SKIPOLE.inputtext.TextInput1.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.inputtext.TextInput1.prototype.constructor = SKIPOLE.inputtext.TextInput1;
SKIPOLE.inputtext.TextInput1.prototype.setvalues = function (fieldlist, result) {
    if (!this.widg_id) {
        return;
        }
    this.set_accepted_errored(this.widg, fieldlist, result);
    // input_text
    var input_text = this.fieldarg_in_result('input_text', result, fieldlist);
    if (input_text !== undefined) {
        this.widg.val(input_text);
        }
    };


SKIPOLE.inputtext.Password1 = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    this.display_errors = false;
    };
SKIPOLE.inputtext.Password1.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.inputtext.Password1.prototype.constructor = SKIPOLE.inputtext.Password1;
SKIPOLE.inputtext.Password1.prototype.setvalues = function (fieldlist, result) {
    if (!this.widg_id) {
        return;
        }
    this.set_accepted_errored(this.widg, fieldlist, result);
    // input_text
    var input_text = this.fieldarg_in_result('input_text', result, fieldlist);
    if (input_text !== undefined) {
        this.widg.val(input_text);
        }
    };


SKIPOLE.inputtext.TextInput2 = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    };
SKIPOLE.inputtext.TextInput2.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.inputtext.TextInput2.prototype.constructor = SKIPOLE.inputtext.TextInput2;
SKIPOLE.inputtext.TextInput2.prototype.setvalues = function (fieldlist, result) {
    if (!this.widg_id) {
        return;
        }
    /* check if an error message or clear_error is given */
    this.check_error(fieldlist, result);
    var text_input = this.widg.find('input[type="text"]');
    var input_disabled = this.fieldarg_in_result('disabled', result, fieldlist);
    this.set_if_disabled(text_input, input_disabled, fieldlist, result);
    this.set_accepted_errored(text_input, fieldlist, result);
    // input_text
    var input_text = this.fieldarg_in_result('input_text', result, fieldlist);
    if (input_text !== undefined) {
        text_input.val(input_text);
        }
    };


SKIPOLE.inputtext.Password2 = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    };
SKIPOLE.inputtext.Password2.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.inputtext.Password2.prototype.constructor = SKIPOLE.inputtext.Password2;
SKIPOLE.inputtext.Password2.prototype.setvalues = function (fieldlist, result) {
    if (!this.widg_id) {
        return;
        }
    /* check if an error message or clear_error is given */
    this.check_error(fieldlist, result);
    var text_input = this.widg.find('input[type="password"]');
    var input_disabled = this.fieldarg_in_result('disabled', result, fieldlist);
    this.set_if_disabled(text_input, input_disabled, fieldlist, result);
    this.set_accepted_errored(text_input, fieldlist, result);
    // input_text
    var input_text = this.fieldarg_in_result('input_text', result, fieldlist);
    if (input_text !== undefined) {
        text_input.val(input_text);
        }
    };


SKIPOLE.inputtext.TextInput3 = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    this.display_errors = false;
    };
SKIPOLE.inputtext.TextInput3.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.inputtext.TextInput3.prototype.constructor = SKIPOLE.inputtext.TextInput3;
SKIPOLE.inputtext.TextInput3.prototype.setvalues = function (fieldlist, result) {
    if (!this.widg_id) {
        return;
        }
    var text_input = this.widg.find('input[type="text"]');
    this.set_accepted_errored(text_input, fieldlist, result);
    // input_text
    var input_text = this.fieldarg_in_result('input_text', result, fieldlist);
    if (input_text !== undefined) {
        text_input.val(input_text);
        }
    };


SKIPOLE.inputtext.TextInput4 = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    this.display_errors = false;
    };
SKIPOLE.inputtext.TextInput4.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.inputtext.TextInput4.prototype.constructor = SKIPOLE.inputtext.TextInput4;
SKIPOLE.inputtext.TextInput4.prototype.setvalues = function (fieldlist, result) {
    if (!this.widg_id) {
        return;
        }
    var text_input = this.widg.find('input[type="text"]');
    var input_disabled = this.fieldarg_in_result('disabled', result, fieldlist);
    this.set_if_disabled(text_input, input_disabled, fieldlist, result);
    this.set_accepted_errored(text_input, fieldlist, result);
    // input_text
    var input_text = this.fieldarg_in_result('input_text', result, fieldlist);
    if (input_text !== undefined) {
        text_input.val(input_text);
        }
    };


SKIPOLE.inputtext.SubmitTextInput1 = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    };
SKIPOLE.inputtext.SubmitTextInput1.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.inputtext.SubmitTextInput1.prototype.constructor = SKIPOLE.inputtext.SubmitTextInput1;
SKIPOLE.inputtext.SubmitTextInput1.prototype.setvalues = function (fieldlist, result) {
    if (!this.widg_id) {
        return;
        }
    /* check if an error message or clear_error is given */
    this.check_error(fieldlist, result);
    // sets hidden fields
    this.sethiddenfields(fieldlist, result);
    // sent input text
    var text_input = this.widg.find('input[type="text"]');
    // Check for set_input_accepted or set_input_errored
    this.set_accepted_errored(text_input, fieldlist, result);
    // input_text
    var input_text = this.fieldarg_in_result('input_text', result, fieldlist);
    if (input_text !== undefined) {
        text_input.val(input_text);
        }
    // hide
    var set_hide = this.fieldarg_in_result('hide', result, fieldlist);
    if (set_hide !== undefined) {
        if (set_hide) {
            if (this.widg.is(":visible")) {
                this.widg.fadeOut('slow');
                }
            }
        else {
            if (!(this.widg.is(":visible"))) {
                this.widg.fadeIn('slow');
                 }
            }
        }
    };
SKIPOLE.inputtext.SubmitTextInput1.prototype.eventfunc = function (e) {
    if (e.type == 'submit') {
        // form submitted
        if (!SKIPOLE.form_validate(this.widg)) {
            // prevent the submission if validation failure
            e.preventDefault();
            }
        else {
            // form validated, so if json url set, call a json page
            var jsonurl = this.fieldvalues["url"];
            if (jsonurl) {
                var self = this;
                var widgform = this.widg.find('form');
                var senddata = widgform.serializeArray();
                e.preventDefault();
                // respond to json or html
                $.ajax({
                      url: jsonurl,
                      data: senddata
                          })
                      .done(function(result, textStatus, jqXHR) {
                         if (jqXHR.responseJSON) {
                              // JSON response
                              if (self.get_error(result)) {
                                  // if error, set any results received from the json call
                                  SKIPOLE.setfields(result);
                                  }
                              else {
                                  // If no error received, clear any previous error
                                  self.clear_error();
                                  SKIPOLE.setfields(result);
                                  // enable input event, which is used to clear set_accepted class on input
                                  self.widg.on('input', function(e) {self.eventfunc(e)});
                                  }
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
            }
        }
    else if (e.type == 'input'){
        // text changed in input field
        this.widg.off(e);
        this.set_accepted($(e.target),false);
        }
    };
SKIPOLE.inputtext.SubmitTextInput1.prototype.show_error = function (error_message) {
    if (!this.display_errors) {
        return;
        }
    SKIPOLE.BaseWidget.prototype.show_error.call(this, error_message);
    var input_field = this.widg.find('input[type="text"]');
    this.set_errored(input_field, true);
    };
SKIPOLE.inputtext.SubmitTextInput1.prototype.clear_error = function() {
    if (!this.display_errors) {
        return;
        }
    SKIPOLE.BaseWidget.prototype.clear_error.call(this);
    var input_field = this.widg.find('input[type="text"]');
    this.set_errored(input_field, false);
    };


SKIPOLE.inputtext.SubmitTextInput3 = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    };
SKIPOLE.inputtext.SubmitTextInput3.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.inputtext.SubmitTextInput3.prototype.constructor = SKIPOLE.inputtext.SubmitTextInput3;
SKIPOLE.inputtext.SubmitTextInput3.prototype.setvalues = function (fieldlist, result) {
    if (!this.widg_id) {
        return;
        }
    /* check if an error message or clear_error is given */
    this.check_error(fieldlist, result);
    // sets hidden fields
    this.sethiddenfields(fieldlist, result);
    // set text input
    var text_input = this.widg.find('input[type="text"]');
    // Check for set_input_accepted or set_input_errored
    this.set_accepted_errored(text_input, fieldlist, result);
    // div2 is the second div of the widget holding the paragraphs
    var div2 = this.widg.find("div:eq(1)");
    var para1 = div2.find(':first');
    // para_text
    var para_text = this.fieldarg_in_result('para_text', result, fieldlist);
    if (para_text !== undefined) {
        para1.text(para_text);
        }
    // show_para1
    var show_para1 = this.fieldarg_in_result('show_para1', result, fieldlist);
    if (show_para1 != undefined) {
        if (show_para1) {
            if (!(para1.is(":visible"))) {
                para1.fadeIn('slow');
                 }
             }
        else {
             if (para1.is(":visible")) {
                para1.fadeOut('slow');
                }
            }
        }
    // show_para2
    var show_para2 = this.fieldarg_in_result('show_para2', result, fieldlist);
    if (show_para2 != undefined) {
        var para2 = div2.find(':eq(1)');
        if (show_para2) {
            if (!(para2.is(":visible"))) {
                para2.fadeIn('slow');
                 }
             }
        else {
             if (para2.is(":visible")) {
                para2.fadeOut('slow');
                }
            }
        }
    // input_text
    var input_text = this.fieldarg_in_result('input_text', result, fieldlist);
    if (input_text !== undefined) {
        text_input.val(input_text);
        }
    // hide
    var set_hide = this.fieldarg_in_result('hide', result, fieldlist);
    if (set_hide !== undefined) {
        if (set_hide) {
            if (this.widg.is(":visible")) {
                this.widg.fadeOut('slow');
                }
            }
        else {
            if (!(this.widg.is(":visible"))) {
                this.widg.fadeIn('slow');
                 }
            }
        }
    };
SKIPOLE.inputtext.SubmitTextInput3.prototype.eventfunc = function (e) {
    if (e.type == 'submit') {
        // form submitted
        if (!SKIPOLE.form_validate(this.widg)) {
            // prevent the submission if validation failure
            e.preventDefault();
            }
        else {
            // form validated, so if json url set, call a json page
            var jsonurl = this.fieldvalues["url"];
            if (jsonurl) {
                var self = this
                var widgform = this.widg.find('form');
                var senddata = widgform.serializeArray();
                e.preventDefault();
                // respond to json or html
                $.ajax({
                      url: jsonurl,
                      data: senddata
                          })
                      .done(function(result, textStatus, jqXHR) {
                         if (jqXHR.responseJSON) {
                              // JSON response
                              if (self.get_error(result)) {
                                  // if error, set any results received from the json call
                                  SKIPOLE.setfields(result);
                                  }
                              else {
                                  // If no error received, clear any previous error
                                  self.clear_error();
                                  SKIPOLE.setfields(result);
                                  // enable input event, which is used to clear set_accepted class on input
                                  self.widg.on('input', function(e) {self.eventfunc(e)});
                                  }
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
            }
        }
    else if (e.type == 'input'){
        // text changed in input field
        this.widg.off(e);
        this.set_accepted($(e.target),false);
        }
    };
SKIPOLE.inputtext.SubmitTextInput3.prototype.show_error = function (error_message) {
    if (!this.display_errors) {
        return;
        }
    SKIPOLE.BaseWidget.prototype.show_error.call(this, error_message);
    var input_field = this.widg.find('input[type="text"]');
    this.set_errored(input_field, true);
    };
SKIPOLE.inputtext.SubmitTextInput3.prototype.clear_error = function() {
    if (!this.display_errors) {
        return;
        }
    SKIPOLE.BaseWidget.prototype.clear_error.call(this);
    var input_field = this.widg.find('input[type="text"]');
    this.set_errored(input_field, false);
    };


SKIPOLE.inputtext.TwoInputsSubmit1 = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    };
SKIPOLE.inputtext.TwoInputsSubmit1.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.inputtext.TwoInputsSubmit1.prototype.constructor = SKIPOLE.inputtext.TwoInputsSubmit1;
SKIPOLE.inputtext.TwoInputsSubmit1.prototype.setvalues = function (fieldlist, result) {
    if (!this.widg_id) {
        return;
        }
    /* check if an error message or clear_error is given */
    this.check_error(fieldlist, result);
    // sets hidden fields
    this.sethiddenfields(fieldlist, result);
    // input 1
    var text1 = this.widg.find('input:first');
    // Check for set_input_accepted1 or set_input_errored1
    var input_accepted1 = this.fieldarg_in_result('set_input_accepted1', result, fieldlist);
    this.set_accepted(text1, input_accepted1);
    var input_errored1 = this.fieldarg_in_result('set_input_errored1', result, fieldlist);
    this.set_errored(text1, input_errored1);
    // input_text1
    var input_text1 = this.fieldarg_in_result('input_text1', result, fieldlist);
    if (input_text1 !== undefined) {
        text1.val(input_text1);
        }
    // input 2
    var text2 = this.widg.find('input:eq(1)');
    // Check for set_input_accepted2 or set_input_errored2
    var input_accepted2 = this.fieldarg_in_result('set_input_accepted2', result, fieldlist);
    this.set_accepted(text2, input_accepted2);
    var input_errored2 = this.fieldarg_in_result('set_input_errored2', result, fieldlist);
    this.set_errored(text2, input_errored2);
    // input_text2
    var input_text2 = this.fieldarg_in_result('input_text2', result, fieldlist);
    if (input_text2 !== undefined) {
        text2.val(input_text2);
        }
    };
SKIPOLE.inputtext.TwoInputsSubmit1.prototype.eventfunc = function (e) {
    if (e.type == 'submit') {
        // form submitted
        if (!SKIPOLE.form_validate(this.widg)) {
            // prevent the submission if validation failure
            e.preventDefault();
            }
        else {
            // form validated, so if json url set, call a json page
            var jsonurl = this.fieldvalues["url"];
            if (jsonurl) {
                var self = this
                var widgform = this.widg.find('form');
                var senddata = widgform.serializeArray();
                e.preventDefault();
                // respond to json or html
                $.ajax({
                      url: jsonurl,
                      data: senddata
                          })
                      .done(function(result, textStatus, jqXHR) {
                         if (jqXHR.responseJSON) {
                              // JSON response
                              if (self.get_error(result)) {
                                  // if error, set any results received from the json call
                                  SKIPOLE.setfields(result);
                                  }
                              else {
                                  // If no error received, clear any previous error
                                  self.clear_error();
                                  SKIPOLE.setfields(result);
                                  // enable input event, which is used to clear set_accepted class on input
                                  self.widg.on('input', function(e) {self.eventfunc(e)});
                                  }
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
            }
        }
    else if (e.type == 'input'){
        // text changed in input field
        this.widg.off(e);
        this.set_accepted($(e.target),false);
        }
    };
SKIPOLE.inputtext.TwoInputsSubmit1.prototype.clear_error = function() {
    if (!this.display_errors) {
        return;
        }
    SKIPOLE.BaseWidget.prototype.clear_error.call(this);
    var text1 = this.widg.find('input:first');
    this.set_errored(text1, false);
    var text2 = this.widg.find('input:eq(1)');
    this.set_errored(text2, false);
    };


SKIPOLE.inputtext.SubmitDict1 = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    this.display_errors = false;
    };
SKIPOLE.inputtext.SubmitDict1.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.inputtext.SubmitDict1.prototype.constructor = SKIPOLE.inputtext.SubmitDict1;
SKIPOLE.inputtext.SubmitDict1.prototype.setvalues = function (fieldlist, result) {
    if (!this.widg_id) {
        return;
        }
    // sets hidden fields
    this.sethiddenfields(fieldlist, result);
    };



SKIPOLE.inputtext.SubmitTextInput2 = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    };
SKIPOLE.inputtext.SubmitTextInput2.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.inputtext.SubmitTextInput2.prototype.constructor = SKIPOLE.inputtext.SubmitTextInput2;
SKIPOLE.inputtext.SubmitTextInput2.prototype.setvalues = function (fieldlist, result) {
    if (!this.widg_id) {
        return;
        }
    /* check if an error message or clear_error is given */
    this.check_error(fieldlist, result);
    // session_storage
    var sessionkey = this.fieldarg_in_result('session_storage', result, fieldlist);
    if (sessionkey) {
        this.fieldvalues["session_storage"] = sessionkey;
        }
    // local_storage
    var localkey = this.fieldarg_in_result('local_storage', result, fieldlist);
    if (localkey) {
        this.fieldvalues["local_storage"] = localkey;
        }
    var text_input = this.widg.find('input[type="text"]');
    // Check for set_input_accepted or set_input_errored
    this.set_accepted_errored(text_input, fieldlist, result);
    // input_text
    var input_text = this.fieldarg_in_result('input_text', result, fieldlist);
    if (input_text !== undefined) {
        text_input.val(input_text);
        }

    // sets hidden fields
    this.sethiddenfields(fieldlist, result);

    // hide
    var set_hide = this.fieldarg_in_result('hide', result, fieldlist);
    if (set_hide !== undefined) {
        if (set_hide) {
            if (this.widg.is(":visible")) {
                this.widg.fadeOut('slow');
                }
            }
        else {
            if (!(this.widg.is(":visible"))) {
                this.widg.fadeIn('slow');
                 }
            }
        }
    };
SKIPOLE.inputtext.SubmitTextInput2.prototype.eventfunc = function (e) {
    if (e.type == 'submit') {
        // form submitted
        e.preventDefault();
        var selected_form = $(e.target);
        if (!SKIPOLE.form_validate(selected_form)) {
            return;
            }

        // Get the url to call
        var url = this.fieldvalues["url"];
        if (!url) {
            url = selected_form.attr('action');
            }
        if (!url) {
            return;
            }

        // url set, send data
        var self = this
        var senddata = new FormData(selected_form[0]);

        var sessionkey = this.fieldvalues["session_storage"];
        var localkey = this.fieldvalues["local_storage"];

        if (sessionkey || localkey) {
            // set stored data into senddata
            if (typeof(Storage) !== "undefined") {

                if (sessionkey) {
                    // get the key value from storage
                    let s_keyvalue = sessionStorage.getItem(sessionkey);
                    if (s_keyvalue != null) {
                        senddata.append(this.formname("session_storage"), s_keyvalue);
                        }
                    }
                if (localkey) {
                    // get the key value from storage
                    let l_keyvalue = localStorage.getItem(localkey);
                    if (l_keyvalue != null) {
                        senddata.append(this.formname("local_storage"), l_keyvalue);
                        }
                    }

                }
            }

        // Display the key/value pairs in senddata
        // for (var pair of senddata.entries()) {
        //    console.log(pair[0]+ ', ' + pair[1]); 
        // }


        // respond to json or html
        $.ajax({
              url: url,
              data: senddata,
              processData: false,
              contentType: false,
              type: 'POST'
                  })
              .done(function(result, textStatus, jqXHR) {
                 if (jqXHR.responseJSON) {
                      // JSON response
                      if (self.get_error(result)) {
                          // if error, set any results received from the json call
                          SKIPOLE.setfields(result);
                          }
                      else {
                          // If no error received, clear any previous error
                          self.clear_error();
                          SKIPOLE.setfields(result);
                          // enable input event, which is used to clear set_accepted class on input
                          self.widg.on('input', function(e) {self.eventfunc(e)});
                          }
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
    else if (e.type == 'input'){
        // text changed in input field
        this.widg.off(e);
        this.set_accepted($(e.target),false);
        }
    };
SKIPOLE.inputtext.SubmitTextInput2.prototype.show_error = function (error_message) {
    if (!this.display_errors) {
        return;
        }
    SKIPOLE.BaseWidget.prototype.show_error.call(this, error_message);
    var input_field = this.widg.find('input[type="text"]');
    this.set_errored(input_field, true);
    };
SKIPOLE.inputtext.SubmitTextInput2.prototype.clear_error = function() {
    if (!this.display_errors) {
        return;
        }
    SKIPOLE.BaseWidget.prototype.clear_error.call(this);
    var input_field = this.widg.find('input[type="text"]');
    this.set_errored(input_field, false);
    };

