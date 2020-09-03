
SKIPOLE.inputforms = {};

SKIPOLE.inputforms.HiddenField = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    this.display_errors = false;
    };
SKIPOLE.inputforms.HiddenField.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.inputforms.HiddenField.prototype.constructor = SKIPOLE.inputforms.HiddenField;
SKIPOLE.inputforms.HiddenField.prototype.setvalues = function (fieldlist, result) {
    if (!this.widg_id) {
        return;
        }
    // value
    var value = this.fieldarg_in_result('hidden_field', result, fieldlist);
    if (value) {
        this.widg.attr("value", value);
        }
    };


SKIPOLE.inputforms.HiddenSessionStorage = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    this.display_errors = false;
    if ( SKIPOLE.widget_register.hasOwnProperty("inputforms.HiddenSessionStorage") ) {
        SKIPOLE.widget_register["inputforms.HiddenSessionStorage"].push(widg_id);
        }
    else {
        SKIPOLE.widget_register["inputforms.HiddenSessionStorage"] = [widg_id];
        }
    };
SKIPOLE.inputforms.HiddenSessionStorage.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.inputforms.HiddenSessionStorage.prototype.constructor = SKIPOLE.inputforms.HiddenSessionStorage;
SKIPOLE.inputforms.HiddenSessionStorage.prototype.setvalues = function (fieldlist, result) {
    if (!this.widg_id) {
        return;
        }
    if (typeof(Storage) !== "undefined") {
            // get the key, and its value from storage
            var thekey = this.fieldarg_in_result('session_key', result, fieldlist);
            var keyvalue = sessionStorage.getItem(thekey);
            if (keyvalue !== "undefined") {
                this.widg.attr("value", keyvalue);
                this.fieldvalues["session_key"] = thekey
                }
        }
    };
SKIPOLE.inputforms.HiddenSessionStorage.prototype.updatefunc = function () {
    if (typeof(Storage) !== "undefined") {
        var thekey = this.fieldvalues["session_key"];
        var keyvalue = sessionStorage.getItem(thekey);
        if (keyvalue !== "undefined") {
            this.widg.attr("value", keyvalue);
            }
        }
    };


SKIPOLE.inputforms.HiddenLocalStorage = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    this.display_errors = false;
    if ( SKIPOLE.widget_register.hasOwnProperty("inputforms.HiddenLocalStorage") ) {
        SKIPOLE.widget_register["inputforms.HiddenLocalStorage"].push(widg_id);
        }
    else {
        SKIPOLE.widget_register["inputforms.HiddenLocalStorage"] = [widg_id];
        }
    };
SKIPOLE.inputforms.HiddenLocalStorage.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.inputforms.HiddenLocalStorage.prototype.constructor = SKIPOLE.inputforms.HiddenLocalStorage;
SKIPOLE.inputforms.HiddenLocalStorage.prototype.setvalues = function (fieldlist, result) {
    if (!this.widg_id) {
        return;
        }
    if (typeof(Storage) !== "undefined") {
            // get the key, and its value from storage
            var thekey = this.fieldarg_in_result('local_key', result, fieldlist);
            var keyvalue = localStorage.getItem(thekey);
            if (keyvalue !== "undefined") {
                this.widg.attr("value", keyvalue);
                this.fieldvalues["local_key"] = thekey
                }
        }
    };
SKIPOLE.inputforms.HiddenLocalStorage.prototype.updatefunc = function () {
    if (typeof(Storage) !== "undefined") {
        var thekey = this.fieldvalues["local_key"];
        var keyvalue = localStorage.getItem(thekey);
        if (keyvalue !== "undefined") {
            this.widg.attr("value", keyvalue);
            }
        }
    };


SKIPOLE.inputforms.SubmitButton1 = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    this.display_errors = false;
    };
SKIPOLE.inputforms.SubmitButton1.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.inputforms.SubmitButton1.prototype.constructor = SKIPOLE.inputforms.SubmitButton1;
SKIPOLE.inputforms.SubmitButton1.prototype.setvalues = function (fieldlist, result) {
    if (!this.widg_id) {
        return;
        }
    // button_text
    var button_text = this.fieldarg_in_result('button_text', result, fieldlist);
    if (button_text) {
        this.widg.attr("value", button_text);
        }
    };


SKIPOLE.inputforms.SubmitButton2 = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    this.display_errors = false;
    };
SKIPOLE.inputforms.SubmitButton2.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.inputforms.SubmitButton2.prototype.constructor = SKIPOLE.inputforms.SubmitButton2;
SKIPOLE.inputforms.SubmitButton2.prototype.setvalues = function (fieldlist, result) {
    if (!this.widg_id) {
        return;
        }
    // button_text
    var button_text = this.fieldarg_in_result('button_text', result, fieldlist);
    if (button_text) {
        this.widg.attr("value", button_text);
        }
    };


SKIPOLE.inputforms.Form1 = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    };
SKIPOLE.inputforms.Form1.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.inputforms.Form1.prototype.constructor = SKIPOLE.inputforms.Form1;
SKIPOLE.inputforms.Form1.prototype.setvalues = function (fieldlist, result) {
    if (!this.widg_id) {
        return;
        }
    // sets hidden fields
    this.sethiddenfields(fieldlist, result);
    };
SKIPOLE.inputforms.Form1.prototype.eventfunc = function(e) {
    var selected_form = $(e.target);
    if (!SKIPOLE.form_validate(selected_form)) {
        // prevent the submission if validation failure
        e.preventDefault();
        }
    };


SKIPOLE.inputforms.SubmitForm1 = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    };
SKIPOLE.inputforms.SubmitForm1.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.inputforms.SubmitForm1.prototype.constructor = SKIPOLE.inputforms.SubmitForm1;
SKIPOLE.inputforms.SubmitForm1.prototype.setvalues = function (fieldlist, result) {
    if (!this.widg_id) {
        return;
        }
    // sets hidden fields
    this.sethiddenfields(fieldlist, result);
    };

SKIPOLE.inputforms.SubmitForm1.prototype.eventfunc = function(e) {
    var selected_form = $(e.target);
    if (!SKIPOLE.form_validate(selected_form)) {
        // prevent the submission if validation failure
        e.preventDefault();
        }
    else {
        // form validated, set please wait message on button
        var btn = $("#" + this.fieldvalues["buttonident"]);
        var buttontext = btn.attr("value");
        // set button_wait_text
        var button_wait_text = this.fieldvalues["button_wait_text"]
        if (button_wait_text) {
            btn.attr("value", button_wait_text);
            }
        // if action_json url set, call a json page
        var jsonurl = this.fieldvalues["url"];
        if (jsonurl) {
            // json url set, send data with a request for json and prevent default
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
                              if (btn.attr("value") == button_wait_text) {
                                   btn.attr("value", buttontext);
                                   }
                              }
                          else {
                              // If no error received, clear any previous error
                              self.clear_error();
                              SKIPOLE.setfields(result);
                              if (btn.attr("value") == button_wait_text) {
                                   btn.attr("value", buttontext);
                                   }
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
                                  if (btn.attr("value") == button_wait_text) {
                                      btn.attr("value", buttontext);
                                      }
                                  SKIPOLE.json_failed( jqXHR, textStatus, errorThrown );
                                  }
                      });
            }
        }
    };



SKIPOLE.inputforms.SubmitForm2 = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    };
SKIPOLE.inputforms.SubmitForm2.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.inputforms.SubmitForm2.prototype.constructor = SKIPOLE.inputforms.SubmitForm2;
SKIPOLE.inputforms.SubmitForm2.prototype.setvalues = function (fieldlist, result) {
    if (!this.widg_id) {
        return;
        }

    // sets hidden fields
    this.sethiddenfields(fieldlist, result);

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
    };

SKIPOLE.inputforms.SubmitForm2.prototype.eventfunc = function(e) {
    var selected_form = $(e.target);
    if (!SKIPOLE.form_validate(selected_form)) {
        // prevent the submission if validation failure
        e.preventDefault();
        return;
        }

    // form validated, set please wait message on button
    var btn = $("#" + this.fieldvalues["buttonident"]);
    var buttontext = btn.attr("value");
    // set button_wait_text
    var button_wait_text = this.fieldvalues["button_wait_text"]
    if (button_wait_text) {
        btn.attr("value", button_wait_text);
        }

    // Get the url to call
    var url = this.fieldvalues["url"];
    if (!url) {
        url = selected_form.attr('action');
        }
    if (!url) {
        e.preventDefault();
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


    e.preventDefault();
    // respond to json or html
    $.ajax({
          url: url,
          data: senddata,
          processData: false,
          contentType: false,
          type: 'POST',
              })
          .done(function(result, textStatus, jqXHR) {
             if (jqXHR.responseJSON) {
                  // JSON response
                  if (self.get_error(result)) {
                      // if error, set any results received from the json call
                      SKIPOLE.setfields(result);
                      if (btn.attr("value") == button_wait_text) {
                           btn.attr("value", buttontext);
                           }
                      }
                  else {
                      // If no error received, clear any previous error
                      self.clear_error();
                      SKIPOLE.setfields(result);
                      if (btn.attr("value") == button_wait_text) {
                           btn.attr("value", buttontext);
                           }
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
                          if (btn.attr("value") == button_wait_text) {
                              btn.attr("value", buttontext);
                              }
                          SKIPOLE.json_failed( jqXHR, textStatus, errorThrown );
                          }
              });
    };


