

SKIPOLE.links = {};

SKIPOLE.links.Link = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    this.display_errors = false;
    };
SKIPOLE.links.Link.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.links.Link.prototype.constructor = SKIPOLE.links.Link;
SKIPOLE.links.Link.prototype.setvalues = function (fieldlist, result) {
    if (!this.widg_id) {
        return;
        }
    var the_widg = this.widg;
    // content
    var content = this.fieldarg_in_result('content', result, fieldlist);
    if (content) {
        the_widg.text(content);
        }
    /* get_field1 */
    var get_field1 = this.fieldarg_in_result('get_field1', result, fieldlist);
    if (get_field1 != undefined) {
        var href = the_widg.attr('href');
        var url = this.setgetfield(href, 'get_field1', get_field1);
        the_widg.attr('href', url);
        }
    /* get_field2 */
    var get_field2 = this.fieldarg_in_result('get_field2', result, fieldlist);
    if (get_field2 != undefined) {
        var href = the_widg.attr('href');
        var url = this.setgetfield(href, 'get_field2', get_field2);
        the_widg.attr('href', url);
        }
    };


SKIPOLE.links.ContainerLink1 = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    this.display_errors = false;
    };
SKIPOLE.links.ContainerLink1.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.links.ContainerLink1.prototype.constructor = SKIPOLE.links.ContainerLink1;
SKIPOLE.links.ContainerLink1.prototype.setvalues = function (fieldlist, result) {
    if (!this.widg_id) {
        return;
        }
    var the_widg = this.widg;
    /* get_field1 */
    var get_field1 = this.fieldarg_in_result('get_field1', result, fieldlist);
    if (get_field1 != undefined) {
        var href = the_widg.attr('href');
        var url = this.setgetfield(href, 'get_field1', get_field1);
        the_widg.attr('href', url);
        }
    /* get_field2 */
    var get_field2 = this.fieldarg_in_result('get_field2', result, fieldlist);
    if (get_field2 != undefined) {
        var href = the_widg.attr('href');
        var url = this.setgetfield(href, 'get_field2', get_field2);
        the_widg.attr('href', url);
        }
    };


SKIPOLE.links.ContainerLink2 = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    this.display_errors = false;
    };
SKIPOLE.links.ContainerLink2.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.links.ContainerLink2.prototype.constructor = SKIPOLE.links.ContainerLink2;
SKIPOLE.links.ContainerLink2.prototype.setvalues = function (fieldlist, result) {
    if (!this.widg_id) {
        return;
        }
    var the_widg = this.widg;
    /* get_field1 */
    var get_field1 = this.fieldarg_in_result('get_field1', result, fieldlist);
    if (get_field1 != undefined) {
        var href = the_widg.attr('href');
        var url = this.setgetfield(href, 'get_field1', get_field1);
        the_widg.attr('href', url);
        }
    /* get_field2 */
    var get_field2 = this.fieldarg_in_result('get_field2', result, fieldlist);
    if (get_field2 != undefined) {
        var href = the_widg.attr('href');
        var url = this.setgetfield(href, 'get_field2', get_field2);
        the_widg.attr('href', url);
        }
    };
SKIPOLE.links.ContainerLink2.prototype.eventfunc = function (e) {
    if (!this.widg_id) {
        return;
        }
    var fieldvalues = this.fieldvalues;
    if (!fieldvalues["url"]) {
        // no json url, return and call html link
        return;
        }
    var href = this.widg.attr('href');
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



SKIPOLE.links.LinkToWidget = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    this.display_errors = false;
    };
SKIPOLE.links.LinkToWidget.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.links.LinkToWidget.prototype.constructor = SKIPOLE.links.LinkToWidget;
SKIPOLE.links.LinkToWidget.prototype.setvalues = function (fieldlist, result) {
    if (!this.widg_id) {
        return;
        }
    // content
    var content = this.fieldarg_in_result('content', result, fieldlist);
    if (content) {
        this.widg.text(content);
        }
    /* towidget */
    var towidget = this.fieldarg_in_result('towidget', result, fieldlist);
    if (towidget) {
        var commaindex = towidget.indexOf(',');
        if (commaindex === -1) {
            // no comma
            var widget_id = towidget.trim()
            }
         else {
            var sw = towidget.split(',');
            var widget_id = sw[0].trim() + '-' + sw[1].trim();
            }      
        this.widg.attr('href', '#' + widget_id);
        }
    };


SKIPOLE.links.ImageOrTextLink = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    this.display_errors = false;
    };
SKIPOLE.links.ImageOrTextLink.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.links.ImageOrTextLink.prototype.constructor = SKIPOLE.links.ImageOrTextLink;



SKIPOLE.links.IconLink = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    this.display_errors = false;
    };
SKIPOLE.links.IconLink.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.links.IconLink.prototype.constructor = SKIPOLE.links.IconLink;


SKIPOLE.links.JSONButtonLink = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    };
SKIPOLE.links.JSONButtonLink.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.links.JSONButtonLink.prototype.constructor = SKIPOLE.links.JSONButtonLink;
SKIPOLE.links.JSONButtonLink.prototype.clear_error = function () {
    if (!this.widg_id) {
        return;
        }
    var the_widg = this.widg;
    the_widg.removeAttr("data-status");
    // set the widget class to widget_class
    var widget_class = this.fieldarg_in_result('widget_class', result, fieldlist);
    if (widget_class) {
        the_widg.attr('class', widget_class);
        }
    };
SKIPOLE.links.JSONButtonLink.prototype.show_error = function (error_message) {
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
    the_widg.text(error_message);
    // set the widget class to error class
    var error_class = this.fieldarg_in_result('error_class', result, fieldlist);
    if (error_class) {
        the_widg.attr('class', error_class);
        }
    if (!(the_widg.is(":visible"))) {
         the_widg.fadeIn('slow');
        }
    };
SKIPOLE.links.JSONButtonLink.prototype.setvalues = function (fieldlist, result) {
    if (!this.widg_id) {
        return;
        }
    var the_widg = this.widg;
    /* check if an error message or clear_error is given */
    if (this.check_error(fieldlist, result)) {
        return;
        }
    var button_text = this.fieldarg_in_result('button_text', result, fieldlist);
    if (button_text) {
        the_widg.text(button_text);
        }
    /* get_field1 */
    var get_field1 = this.fieldarg_in_result('get_field1', result, fieldlist);
    if (get_field1 != undefined) {
        var href = the_widg.attr('href');
        var url = this.setgetfield(href, 'get_field1', get_field1);
        the_widg.attr('href', url);
        }
    /* get_field2 */
    var get_field2 = this.fieldarg_in_result('get_field2', result, fieldlist);
    if (get_field2 != undefined) {
        var href = the_widg.attr('href');
        var url = this.setgetfield(href, 'get_field2', get_field2);
        the_widg.attr('href', url);
        }
    /* hide */
    var set_hide = this.fieldarg_in_result('hide', result, fieldlist);
    if (set_hide != undefined) {
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

SKIPOLE.links.JSONButtonLink.prototype.eventfunc = function (e) {
    if (!this.widg_id) {
        return;
        }
    var fieldvalues = this.fieldvalues;

    if (fieldvalues["json_url"]) {
        var sendurl = fieldvalues["json_url"];
        }
    else {
        var sendurl = fieldvalues["html_url"];
        }

    var the_widg = this.widg;
    var href = the_widg.attr('href');
    var buttontext = the_widg.text();
    var button_wait_text = fieldvalues["button_wait_text"]
    the_widg.text(button_wait_text);

    var sessionkey = fieldvalues["session_storage"];
    var localkey = fieldvalues["local_storage"];

    if (sessionkey || localkey) {
        // set stored data into senddata
        var senddata = {};
        if (typeof(Storage) !== "undefined") {

            if (sessionkey) {
                // get the key value from storage
                let s_keyvalue = sessionStorage.getItem(sessionkey);
                if (s_keyvalue != null) {
                    senddata[this.formname("session_storage")] = s_keyvalue;
                    }
                }
            if (localkey) {
                // get the key value from storage
                let l_keyvalue = localStorage.getItem(localkey);
                if (l_keyvalue != null) {
                    senddata[this.formname("local_storage")] = l_keyvalue;
                    }
                }

            }
        // must also send ident here, and the link get value
        let qstring = href.substring(href.indexOf('?')+1);
        let params = new URLSearchParams(qstring);
        senddata["ident"] = params.get("ident");
        if ( params.get(this.formname("get_field1"))) {
            senddata[this.formname("get_field1")] = params.get(this.formname("get_field1"));
            }
        if ( params.get(this.formname("get_field2"))) {
            senddata[this.formname("get_field2")] = params.get(this.formname("get_field2"));
            }
        }
    else {
        // no stored data to send
        var senddata = href.substring(href.indexOf('?')+1);
        }

    e.preventDefault();
    // respond to json or html
    $.ajax({
          url: sendurl,
          data: senddata,
          method: "POST"
              })
          .done(function(result, textStatus, jqXHR) {
             if (jqXHR.responseJSON) {
                  // JSON response
                  SKIPOLE.setfields(result);
                  if (the_widg.text() == button_wait_text) {
                      the_widg.text(buttontext);
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
                          if (the_widg.text() == button_wait_text) {
                              the_widg.text(buttontext);
                              }
                          SKIPOLE.json_failed( jqXHR, textStatus, errorThrown );
                          }
              });

    };





SKIPOLE.links.ButtonLink1 = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    };
SKIPOLE.links.ButtonLink1.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.links.ButtonLink1.prototype.constructor = SKIPOLE.links.ButtonLink1;
SKIPOLE.links.ButtonLink1.prototype.clear_error = function () {
    if (!this.widg_id) {
        return;
        }
    var the_widg = this.widg;
    the_widg.removeAttr("data-status");
    // set the widget class to widget_class
    var widget_class = this.fieldarg_in_result('widget_class', result, fieldlist);
    if (widget_class) {
        the_widg.attr('class', widget_class);
        }
    };
SKIPOLE.links.ButtonLink1.prototype.show_error = function (error_message) {
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
    the_widg.text(error_message);
    // set the widget class to error class
    var error_class = this.fieldarg_in_result('error_class', result, fieldlist);
    if (error_class) {
        the_widg.attr('class', error_class);
        }
    if (!(the_widg.is(":visible"))) {
         the_widg.fadeIn('slow');
        }
    };
SKIPOLE.links.ButtonLink1.prototype.setvalues = function (fieldlist, result) {
    if (!this.widg_id) {
        return;
        }
    var the_widg = this.widg;
    /* check if an error message or clear_error is given */
    if (this.check_error(fieldlist, result)) {
        return;
        }
    var button_text = this.fieldarg_in_result('button_text', result, fieldlist);
    if (button_text) {
        the_widg.text(button_text);
        }
    var set_hide = this.fieldarg_in_result('hide', result, fieldlist);
    if (set_hide != undefined) {
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


SKIPOLE.links.ButtonLink2 = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    };
SKIPOLE.links.ButtonLink2.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.links.ButtonLink2.prototype.constructor = SKIPOLE.links.ButtonLink2;
SKIPOLE.links.ButtonLink2.prototype.show_error = function (error_message) {
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
    // if widg not visible, show it
    if (!(the_widg.is(":visible"))) {
         the_widg.show();
        }
    // get error div, being first child
    var error_div = the_widg.find(':first');
    var error_para = error_div.find(':first');
    error_para.text(error_message);
    if (!(error_div.is(":visible"))) {
       error_div.show();
        }
    };
SKIPOLE.links.ButtonLink2.prototype.setvalues = function (fieldlist, result) {
    if (!this.widg_id) {
        return;
        }
    var the_widg = this.widg;
    var button_text = this.fieldarg_in_result('button_text', result, fieldlist);
    var a_link = the_widg.find('a');
    if (button_text) {
        a_link.text(button_text);
        }
    /* get_field1 */
    var get_field1 = this.fieldarg_in_result('get_field1', result, fieldlist);
    if (get_field1 != undefined) {
        var href = a_link.attr('href');
        var url = this.setgetfield(href, 'get_field1', get_field1);
        a_link.attr('href', url);
        }
    /* get_field2 */
    var get_field2 = this.fieldarg_in_result('get_field2', result, fieldlist);
    if (get_field2 != undefined) {
        var href = a_link.attr('href');
        var url = this.setgetfield(href, 'get_field2', get_field2);
        a_link.attr('href', url);
        }
    /* check if an error message or clear_error is given */
    if (this.check_error(fieldlist, result)) {
        return;
        }
    var set_hide = this.fieldarg_in_result('hide', result, fieldlist);
    if (set_hide != undefined) {
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
SKIPOLE.links.ButtonLink2.prototype.eventfunc = function (e) {
    if (!this.widg_id) {
        return;
        }
    var fieldvalues = this.fieldvalues;
    var the_widg = this.widg;
    var a_link = the_widg.find('a');
    var buttontext = a_link.text();
   // set button_wait_text
    var button_wait_text = fieldvalues["button_wait_text"]
    if (button_wait_text) {
        a_link.text(button_wait_text);
        }
    if (!fieldvalues["url"]) {
        // no json url, return and call html link
        return;
        }
    var href = a_link.attr('href');
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
                  if (a_link.text() == button_wait_text) {
                       a_link.text(buttontext);
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
                          if (a_link.text() == button_wait_text) {
                              a_link.text(buttontext);
                              }
                          SKIPOLE.json_failed( jqXHR, textStatus, errorThrown );
                          }
              });
    };


SKIPOLE.links.CloseButton = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    this.display_errors = false;
    };
SKIPOLE.links.CloseButton.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.links.CloseButton.prototype.constructor = SKIPOLE.links.CloseButton;
SKIPOLE.links.CloseButton.prototype.eventfunc = function (e) {
    if (!this.widg_id) {
        return;
        }
    var fieldvalues = this.fieldvalues;
    var the_widg = this.widg;
    // get id of target
    var target_section = fieldvalues["target_section"];
    var target_widget = fieldvalues["target_widget"];
    if (target_section && target_widget) {
        var target_id = target_section + "-" + target_widget;
    } else if ( target_section ) {
        var target_id = target_section;
    } else if ( target_widget ) {
        var target_id = target_widget;
    } else {
        var target_id = "";
    }

    if (!target_id) {
        return;
        }
    // close item with target_id
    var target = $("#"+target_id);
    if (target) {
        if (target.is(":visible")) {
            target.hide();
            }
        e.preventDefault();
        }
    };


SKIPOLE.links.OpenButton = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    this.display_errors = false;
    };
SKIPOLE.links.OpenButton.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.links.OpenButton.prototype.constructor = SKIPOLE.links.OpenButton;
SKIPOLE.links.OpenButton.prototype.eventfunc = function (e) {
    if (!this.widg_id) {
        return;
        }
    var fieldvalues = this.fieldvalues;
    var the_widg = this.widg;
    // get id of target
    var target_section = fieldvalues["target_section"];
    var target_widget = fieldvalues["target_widget"];
    if (target_section && target_widget) {
        var target_id = target_section + "-" + target_widget;
    } else if ( target_section ) {
        var target_id = target_section;
    } else if ( target_widget ) {
        var target_id = target_widget;
    } else {
        var target_id = "";
    }

    if (!target_id) {
        return;
        }
    // open item with target_id
    var target = $("#"+target_id);
    if (target) {
        if (!(target.is(":visible"))) {
            target.show();
            }
        e.preventDefault();
        }
    };


SKIPOLE.links.OpenButton2 = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    this.display_errors = false;
    };
SKIPOLE.links.OpenButton2.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.links.OpenButton2.prototype.constructor = SKIPOLE.links.OpenButton2;
SKIPOLE.links.OpenButton2.prototype.setvalues = function (fieldlist, result) {
    if (!this.widg_id) {
        return;
        }
    var the_widg = this.widg;
    // content
    var content = this.fieldarg_in_result('content', result, fieldlist);
    if (content) {
        the_widg.text(content);
        }
    /* get_field1 */
    var get_field1 = this.fieldarg_in_result('get_field1', result, fieldlist);
    if (get_field1 != undefined) {
        var href = the_widg.attr('href');
        var url = this.setgetfield(href, 'get_field1', get_field1);
        the_widg.attr('href', url);
        }
    /* get_field2 */
    var get_field2 = this.fieldarg_in_result('get_field2', result, fieldlist);
    if (get_field2 != undefined) {
        var href = the_widg.attr('href');
        var url = this.setgetfield(href, 'get_field2', get_field2);
        the_widg.attr('href', url);
        }
    /* hide */
    var set_hide = this.fieldarg_in_result('hide', result, fieldlist);
    if (set_hide != undefined) {
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
SKIPOLE.links.OpenButton2.prototype.eventfunc = function (e) {
    if (!this.widg_id) {
        return;
        }
    var fieldvalues = this.fieldvalues;
    var the_widg = this.widg;
    // get id of target
    var target_section = fieldvalues["target_section"];
    var target_widget = fieldvalues["target_widget"];
    if (target_section && target_widget) {
        var target_id = target_section + "-" + target_widget;
    } else if ( target_section ) {
        var target_id = target_section;
    } else if ( target_widget ) {
        var target_id = target_widget;
    } else {
        var target_id = "";
    }

    if (!target_id) {
        return;
        }
    // open item with target_id
    var target = $("#"+target_id);
    if (target) {
        if (!(target.is(":visible"))) {
            target.show();
            }
        e.preventDefault();
        }
    };


SKIPOLE.links.MessageButton = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    this.display_errors = false;
    };
SKIPOLE.links.MessageButton.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.links.MessageButton.prototype.constructor = SKIPOLE.links.ProjectiFrame;

SKIPOLE.links.MessageButton.prototype.setvalues = function (fieldlist, result) {
    if (!this.widg_id) {
        return;
        }
    var fieldvalues = this.fieldvalues;
    var the_widg = this.widg;
    var para_text = this.fieldarg_in_result('para_text', result, fieldlist);
    var messagebox_id = fieldvalues["messagebox_id"];
    if (!messagebox_id) {
        return
        }
    var messagebox = $("#"+messagebox_id);
    var para = messagebox.find('p');
    if (para_text) {
        para.text(para_text);
        }

    var set_hide = this.fieldarg_in_result('hide', result, fieldlist);
    if (set_hide != undefined) {
        if (set_hide) {
            if (messagebox.is(":visible")) {
                messagebox.fadeOut('slow');
                }
            }
        else {
            if (!(messagebox.is(":visible"))) {
                messagebox.fadeIn('slow');
                 }
            }
        }
    };

SKIPOLE.links.MessageButton.prototype.eventfunc = function (e) {
    if (!this.widg_id) {
        return;
        }
    var fieldvalues = this.fieldvalues;
    var the_widg = this.widg;
    // get id of message box
    var messagebox_id = fieldvalues["messagebox_id"];
    if (!messagebox_id) {
        return
        }
    var messagebox = $("#"+messagebox_id);

    var button_pressed = $(e.target);

    if ( button_pressed.is( "button" ) ){
           messagebox.fadeOut('slow');
           return;
           }

    // not the message box button, so it is the link button 
    messagebox.fadeIn('slow');

    if (!fieldvalues["url"]) {
        // no json url, return and call html link
        return;
        }
    var href = button_pressed.attr('href');
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


SKIPOLE.links.Image1 = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    this.display_errors = false;
    };
SKIPOLE.links.Image1.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.links.Image1.prototype.constructor = SKIPOLE.links.Image1;
SKIPOLE.links.Image1.prototype.setvalues = function (fieldlist, result) {
    if (!this.widg_id) {
        return;
        }
    var the_widg = this.widg;
    var fieldvalues = this.fieldvalues;
    var img_url = this.fieldarg_in_result("img_url", result, fieldlist);
    if (img_url) {
        the_widg.attr("src", img_url + "#" + new Date().getTime());
        }
    };


SKIPOLE.links.ImageLink1 = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    this.display_errors = false;
    };
SKIPOLE.links.ImageLink1.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.links.ImageLink1.prototype.constructor = SKIPOLE.links.ImageLink1;


SKIPOLE.links.LinkTextBlockTable1 = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    this.display_errors = false;
    };
SKIPOLE.links.LinkTextBlockTable1.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.links.LinkTextBlockTable1.prototype.constructor = SKIPOLE.links.LinkTextBlockTable1;


SKIPOLE.links.LinkTextBlockTable2 = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    this.display_errors = false;
    };
SKIPOLE.links.LinkTextBlockTable2.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.links.LinkTextBlockTable2.prototype.constructor = SKIPOLE.links.LinkTextBlockTable2;

SKIPOLE.links.ListLinks = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    this.display_errors = false;
    };
SKIPOLE.links.ListLinks.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.links.ListLinks.prototype.constructor = SKIPOLE.links.ListLinks;

SKIPOLE.links.Table1_Button = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    this.display_errors = false;
    };
SKIPOLE.links.Table1_Button.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.links.Table1_Button.prototype.constructor = SKIPOLE.links.Table1_Button;
SKIPOLE.links.Table1_Button.prototype.setvalues = function (fieldlist, result) {
    /* This widget accepts fields - hide */
   if (!this.widg_id) {
        return;
        }
    var the_widg = this.widg;
    var set_hide = this.fieldarg_in_result('hide', result, fieldlist);
    if (set_hide != undefined) {
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
SKIPOLE.links.Table1_Button.prototype.eventfunc = function (e) {
    if (!this.widg_id) {
        return;
        }
    var fieldvalues = this.fieldvalues;
    if (!fieldvalues["url"]) {
        return;
        }
    var href = $(e.target).attr('href');
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


SKIPOLE.links.Table2_Button = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    this.display_errors = false;
    };
SKIPOLE.links.Table2_Button.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.links.Table2_Button.prototype.constructor = SKIPOLE.links.Table2_Button;
SKIPOLE.links.Table2_Button.prototype.setvalues = function (fieldlist, result) {
    /* This widget accepts fields - hide */
   if (!this.widg_id) {
        return;
        }
    var the_widg = this.widg;
    var set_hide = this.fieldarg_in_result('hide', result, fieldlist);
    if (set_hide != undefined) {
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
SKIPOLE.links.Table2_Button.prototype.eventfunc = function (e) {
    if (!this.widg_id) {
        return;
        }
    var fieldvalues = this.fieldvalues;
    if (!fieldvalues["url"]) {
        return;
        }
    var href = $(e.target).attr('href');
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


SKIPOLE.links.Table3_Buttons2 = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    this.display_errors = false;
    };
SKIPOLE.links.Table3_Buttons2.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.links.Table3_Buttons2.prototype.constructor = SKIPOLE.links.Table3_Buttons2;
SKIPOLE.links.Table3_Buttons2.prototype.eventfunc = function (e) {
    if (!this.widg_id) {
        return;
        }
    var fieldvalues = this.fieldvalues;
    var button = $(e.target);
    var buttontext = button.text();
    var myCol = button.parent().index();
    var href = button.attr('href');
    if (!href) {
        return;
        }
    var senddata = href.substring(href.indexOf('?')+1);

    if (myCol === 3) {

       // set button_wait_text
        var button_wait_text = fieldvalues["button_wait_text1"]
        if (button_wait_text) {
            button.text(button_wait_text);
            }

        if (!fieldvalues["url1"]) {
            return;
            }
        // respond to json or html
        e.preventDefault();
        $.ajax({
              url: fieldvalues["url1"],
              data: senddata
                  })
              .done(function(result, textStatus, jqXHR) {
                 if (jqXHR.responseJSON) {
                      // JSON response
                      SKIPOLE.setfields(result);
                      if (button.text() == button_wait_text) {
                          button.text(buttontext);
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
                          if (button.text() == button_wait_text) {
                              button.text(buttontext);
                              }
                          SKIPOLE.json_failed( jqXHR, textStatus, errorThrown );
                          }
                  });
        } else if (myCol === 4) {

            // set button_wait_text
            var button_wait_text = fieldvalues["button_wait_text2"]
            if (button_wait_text) {
                button.text(button_wait_text);
                }

            if (!fieldvalues["url2"]) {
                return;
                }
            // respond to json or html
            e.preventDefault();
            $.ajax({
                  url: fieldvalues["url2"],
                  data: senddata
                      })
                  .done(function(result, textStatus, jqXHR) {
                     if (jqXHR.responseJSON) {
                          // JSON response
                          SKIPOLE.setfields(result);
                          if (button.text() == button_wait_text) {
                              button.text(buttontext);
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
                          if (button.text() == button_wait_text) {
                              button.text(buttontext);
                              }
                          SKIPOLE.json_failed( jqXHR, textStatus, errorThrown );
                          }
                      });
        } else {
            return;
        }
    };


SKIPOLE.links.Table1_Buttons4 = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    this.display_errors = false;
    };
SKIPOLE.links.Table1_Buttons4.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.links.Table1_Buttons4.prototype.constructor = SKIPOLE.links.Table1_Buttons4;


SKIPOLE.links.GeneralButtonTable2 = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    this.display_errors = false;
    };
SKIPOLE.links.GeneralButtonTable2.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.links.GeneralButtonTable2.prototype.constructor = SKIPOLE.links.GeneralButtonTable2;
SKIPOLE.links.GeneralButtonTable2.prototype.eventfunc = function (e) {
    if (!this.widg_id) {
        return;
        }
    var fieldvalues = this.fieldvalues;
    var button = $(e.target);
    var href = button.attr('href');
    if (!href) {
        return;
        }
    if (!fieldvalues["json_url"]) {
        return;
        }
    var senddata = href.substring(href.indexOf('?')+1);
    /* fieldvalues["json_url"] is a list of column json urls
       need to get the column index to find which of these
       urls to send the call to */
    var col = button.parent().index();
    if (!fieldvalues["json_url"][col]) {
        return;
        }
    e.preventDefault();
    // respond to json or html
    $.ajax({
          url: fieldvalues["json_url"][col],
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

SKIPOLE.links.GeneralButtonTable2.prototype.dragstartfunc = function (e, data) {
    e.dataTransfer.setData("text/widgid", this.widg_id);
    e.dataTransfer.setData("text/plain", data);
    };
SKIPOLE.links.GeneralButtonTable2.prototype.dropfunc = function (e, data) {
    e.preventDefault();
    var widg_id = e.dataTransfer.getData("text/widgid");
    if (widg_id != this.widg_id) {
        return;
        }
    var url = this.fieldvalues["dropurl"];
    if (!url) {
        return;
        }
    // now make a call, including data from the drag element and the drop element
    var dragwidgfield = this.formname('dragrows');
    var dropwidgfield = this.formname('droprows');

    var senddata = "ident=" + SKIPOLE.identdata;
    if (data) {
        senddata = senddata + "&" + dropwidgfield + "=" + data;
        }
    if (e.dataTransfer.getData("text/plain")) {
        senddata = senddata + "&" + dragwidgfield + "=" + e.dataTransfer.getData("text/plain");
        }
    $("body").css('cursor','wait');
    // respond to json or html
    $.ajax({
          url: url,
          data: senddata
              })
          .done(function(result, textStatus, jqXHR) {
             if (jqXHR.responseJSON) {
                  // JSON response
                  SKIPOLE.setfields(result);
                  $("body").css('cursor','auto');
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
                          $("body").css('cursor','auto');
                          SKIPOLE.json_failed( jqXHR, textStatus, errorThrown );
                          }
              });
    };
SKIPOLE.links.GeneralButtonTable2.prototype.allowdropfunc = function (e) {
     e.preventDefault();
    };

SKIPOLE.links.GeneralButtonTable2.prototype.setvalues = function (fieldlist, result) {
   if (!this.widg_id) {
        return;
        }
    var widg_id = this.widg_id
    var the_widg = this.widg;
    var fieldvalues = this.fieldvalues;
    // hide the widget
    var set_hide = this.fieldarg_in_result('hide', result, fieldlist);
    if (set_hide != undefined) {
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
    // the class of the button's if any
    var button_class = fieldvalues["button_class"];
    // the class of the rows
    var even_class = fieldvalues["even_class"];
    var odd_class = fieldvalues["odd_class"];
    // get column urls and number of columns
    var json_url = fieldvalues["json_url"];
    var html_url = fieldvalues["html_url"];
    if (json_url == undefined) {
        return;
        }
    if (html_url == undefined) {
        return;
        }
    var cols = html_url.length;
    if (cols != json_url.length) {
        return;
        }
    // cols is the number of columns

    // The table contents
    var contents = this.fieldarg_in_result('contents', result, fieldlist);
    if (contents) {
        // If a request to renew the table is recieved, this bock
        // empties the existing table, and re-draws it
        var rows = Math.floor(contents.length/cols);
        if (rows*cols != contents.length) {
            return;
            }
        // empty the table
        the_widg.empty();
        // and now start filling it again
        var htmlcontent = "";
        var cell = -1;
        for (row = 0; row < rows; row++) {
            // for each row in the table
            // row class
            if (even_class && (row % 2)) {
                htmlcontent += "<tr class = \"" + even_class + "\">";
                }
            else if (odd_class && (!(row % 2))) {
                htmlcontent += "<tr class = \"" + odd_class + "\">";
                }
            else {
                htmlcontent += "<tr>";
                }

            for (col = 0; col < cols; col++) {
                cell += 1;
                var element = contents[cell];
                // cell text
                var celltext = '';
                if (element[0]) {
                    celltext = element[0];
                    }
                // cell style
                if (element[1]) {
                    htmlcontent += "<td " + "style = \"" + element[1] + "\">";
                    }
                else {
                    htmlcontent += "<td>";
                    }
                // get html url for this column
                var url = html_url[col];
                // is it a button link
                if (url && element[2]) {
                    // its a link, apply button class
                    if (button_class) {
                        htmlcontent +=  "<a role = \"button\" class = \"" + button_class + "\"";
                        }
                    else {
                        htmlcontent +=  "<a role = \"button\"";
                        }
                    // get url and create href attribute
                    if (element[3]) {
                        url += "?ident=" + SKIPOLE.identdata + "&" + this.formname("contents") + "=" + element[3];
                        }
                    else {
                        url += "?ident=" + SKIPOLE.identdata
                        }
                    htmlcontent +=  " href = \"" + url + "\">";
                    // apply button text and close <a> tag
                    if (celltext) {
                        htmlcontent += celltext + "</a>";
                        }
                    else {
                        htmlcontent += url + "</a>";
                        }
                    }
                else {
                    // not a link
                    htmlcontent += celltext;
                    }
                // close the cell
                htmlcontent += "</td>";
                }
            htmlcontent += "</tr>";
            }
        the_widg.html(htmlcontent);
        // as table was emptied, a new click event has to be applied to the buttons
        $("#" + widg_id + " a").click(function (e) {
              SKIPOLE.widgets[widg_id].eventfunc(e);
              });
        }
    // dragrows and droprows
    var dragrows = this.fieldarg_in_result('dragrows', result, fieldlist);
    var droprows = this.fieldarg_in_result('droprows', result, fieldlist);
    if (dragrows || droprows) {
        // count the number of rows in the current table
        var tablerows = $("#" + this.widg_id + " tr");
        var rows = tablerows.length;
        }
    else {
        return;
        }
    if (dragrows) {
        if (dragrows.length != rows) {
            return;
            }
        tablerows.each(function( row ) {
            if (dragrows[row][1]) {
                var dragdata = dragrows[row][1];
                }
            else {
                var dragdata = "";
                }
            if (dragrows[row][0]) {
                $(this).attr("style","cursor:move;");
                $(this).attr("draggable","true");
                $(this).attr("ondragstart","SKIPOLE.widgets['" + widg_id + "'].dragstartfunc(event, '" + dragdata + "')");
                }
            else {
                $(this).attr("style",null);
                $(this).attr("draggable",null);
                $(this).attr("ondragstart",null);
                }
            });
        }
    if (droprows) {
        if (droprows.length != rows) {
            return;
            }
        tablerows.each(function( row ) {
            if (droprows[row][1]) {
                var dropdata = droprows[row][1];
                }
            else {
                var dropdata = "";
                }
            if (droprows[row][0]) {
                $(this).attr("ondrop","SKIPOLE.widgets['" + widg_id + "'].dropfunc(event, '" + dropdata + "')");
                $(this).attr("ondragover","SKIPOLE.widgets['" + widg_id + "'].allowdropfunc(event)");
                }
            else {
                $(this).attr("ondrop",null);
                $(this).attr("ondragover",null);
                }
            });
        }
    };


SKIPOLE.links.ProjectiFrame = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    this.display_errors = false;
    };
SKIPOLE.links.ProjectiFrame.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.links.ProjectiFrame.prototype.constructor = SKIPOLE.links.ProjectiFrame;


SKIPOLE.links.GeneralButtonTable1 = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    this.display_errors = false;
    };
SKIPOLE.links.GeneralButtonTable1.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.links.GeneralButtonTable1.prototype.constructor = SKIPOLE.links.GeneralButtonTable1;
SKIPOLE.links.GeneralButtonTable1.prototype.eventfunc = function (e) {
    if (!this.widg_id) {
        return;
        }
    var fieldvalues = this.fieldvalues;
    var button = $(e.target);
    var href = button.attr('href');
    if (!href) {
        return;
        }

    /* fieldvalues["json_url"] is a list of column json urls
       need to get the column index to find which of these
       urls to send the call to */
    var col = button.parent().index();

    if (!fieldvalues["json_url"]) {
        var sendurl = fieldvalues["html_url"][col];
        }
    else if (!fieldvalues["json_url"][col]) {
        var sendurl = fieldvalues["html_url"][col];
        }
    else {
        var sendurl = fieldvalues["json_url"][col];
        }

    var key = fieldvalues["keys"][col];

    if (key) {
        // set stored data into senddata
        var senddata = {};
        if (typeof(Storage) !== "undefined") {
            // get the key value from storage
            var keyvalue = localStorage.getItem(key);
            if (keyvalue != null) {
                senddata[this.formname("cols")] = keyvalue;
                }
            }
        // must also send ident here, and the link get value
        let qstring = href.substring(href.indexOf('?')+1);
        let params = new URLSearchParams(qstring);
        senddata["ident"] = params.get("ident");
        if ( params.get(this.formname("contents"))) {
            senddata[this.formname("contents")] = params.get(this.formname("contents"));
            }
        }
    else {
        var senddata = href.substring(href.indexOf('?')+1);
        }

    e.preventDefault();
    // respond to json or html
    $.ajax({
          url: sendurl,
          data: senddata,
          method: "POST"
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

SKIPOLE.links.GeneralButtonTable1.prototype.dragstartfunc = function (e, data) {
    e.dataTransfer.setData("text/widgid", this.widg_id);
    e.dataTransfer.setData("text/plain", data);
    };
SKIPOLE.links.GeneralButtonTable1.prototype.dropfunc = function (e, data) {
    e.preventDefault();
    var widg_id = e.dataTransfer.getData("text/widgid");
    if (widg_id != this.widg_id) {
        return;
        }
    var url = this.fieldvalues["dropurl"];
    if (!url) {
        return;
        }
    // now make a call, including data from the drag element and the drop element
    var dragwidgfield = this.formname('dragrows');
    var dropwidgfield = this.formname('droprows');

    var senddata = "ident=" + SKIPOLE.identdata;
    if (data) {
        senddata = senddata + "&" + dropwidgfield + "=" + data;
        }
    if (e.dataTransfer.getData("text/plain")) {
        senddata = senddata + "&" + dragwidgfield + "=" + e.dataTransfer.getData("text/plain");
        }
    $("body").css('cursor','wait');
    // respond to json or html
    $.ajax({
          url: url,
          data: senddata
              })
          .done(function(result, textStatus, jqXHR) {
             if (jqXHR.responseJSON) {
                  // JSON response
                  SKIPOLE.setfields(result);
                  $("body").css('cursor','auto');
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
                          $("body").css('cursor','auto');
                          SKIPOLE.json_failed( jqXHR, textStatus, errorThrown );
                          }
              });
    };
SKIPOLE.links.GeneralButtonTable1.prototype.allowdropfunc = function (e) {
     e.preventDefault();
    };

SKIPOLE.links.GeneralButtonTable1.prototype.setvalues = function (fieldlist, result) {
   if (!this.widg_id) {
        return;
        }
    var widg_id = this.widg_id
    var the_widg = this.widg;
    var fieldvalues = this.fieldvalues;
    // hide the widget
    var set_hide = this.fieldarg_in_result('hide', result, fieldlist);
    if (set_hide != undefined) {
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
    // the class of the button's if any
    var button_class = fieldvalues["button_class"];
    // the class of the rows
    var even_class = fieldvalues["even_class"];
    var odd_class = fieldvalues["odd_class"];
    // get column urls and number of columns
    var json_url = fieldvalues["json_url"];
    var html_url = fieldvalues["html_url"];
    var keys = fieldvalues["keys"];
    if (json_url == undefined) {
        return;
        }
    if (html_url == undefined) {
        return;
        }
    if (keys == undefined) {
        return;
        }
    var cols = html_url.length;
    if (cols != json_url.length) {
        return;
        }
    if (cols != keys.length) {
        return;
        }
    // cols is the number of columns

    // The table contents
    var contents = this.fieldarg_in_result('contents', result, fieldlist);
    if (contents) {
        // If a request to renew the table is recieved, this bock
        // empties the existing table, and re-draws it
        var rows = Math.floor(contents.length/cols);
        if (rows*cols != contents.length) {
            return;
            }
        // empty the table
        the_widg.empty();
        // and now start filling it again
        var htmlcontent = "";
        var cell = -1;
        for (row = 0; row < rows; row++) {
            // for each row in the table
            // row class
            if (even_class && (row % 2)) {
                htmlcontent += "<tr class = \"" + even_class + "\">";
                }
            else if (odd_class && (!(row % 2))) {
                htmlcontent += "<tr class = \"" + odd_class + "\">";
                }
            else {
                htmlcontent += "<tr>";
                }

            for (col = 0; col < cols; col++) {
                cell += 1;
                var element = contents[cell];
                // cell text
                var celltext = '';
                if (element[0]) {
                    celltext = element[0];
                    }
                // cell style
                if (element[1]) {
                    htmlcontent += "<td " + "style = \"" + element[1] + "\">";
                    }
                else {
                    htmlcontent += "<td>";
                    }
                // get html url for this column
                var url = html_url[col];
                // is it a button link
                if (url && element[2]) {
                    // its a link, apply button class
                    if (button_class) {
                        htmlcontent +=  "<a role = \"button\" class = \"" + button_class + "\"";
                        }
                    else {
                        htmlcontent +=  "<a role = \"button\"";
                        }
                    // get url and create href attribute
                    if (element[3]) {
                        url += "?ident=" + SKIPOLE.identdata + "&" + this.formname("contents") + "=" + element[3];
                        }
                    else {
                        url += "?ident=" + SKIPOLE.identdata
                        }
                    htmlcontent +=  " href = \"" + url + "\">";
                    // apply button text and close <a> tag
                    if (celltext) {
                        htmlcontent += celltext + "</a>";
                        }
                    else {
                        htmlcontent += url + "</a>";
                        }
                    }
                else {
                    // not a link
                    htmlcontent += celltext;
                    }
                // close the cell
                htmlcontent += "</td>";
                }
            htmlcontent += "</tr>";
            }
        the_widg.html(htmlcontent);
        // as table was emptied, a new click event has to be applied to the buttons
        $("#" + widg_id + " a").click(function (e) {
              SKIPOLE.widgets[widg_id].eventfunc(e);
              });
        }
    // dragrows and droprows
    var dragrows = this.fieldarg_in_result('dragrows', result, fieldlist);
    var droprows = this.fieldarg_in_result('droprows', result, fieldlist);
    if (dragrows || droprows) {
        // count the number of rows in the current table
        var tablerows = $("#" + this.widg_id + " tr");
        var rows = tablerows.length;
        }
    else {
        return;
        }
    if (dragrows) {
        if (dragrows.length != rows) {
            return;
            }
        tablerows.each(function( row ) {
            if (dragrows[row][1]) {
                var dragdata = dragrows[row][1];
                }
            else {
                var dragdata = "";
                }
            if (dragrows[row][0]) {
                $(this).attr("style","cursor:move;");
                $(this).attr("draggable","true");
                $(this).attr("ondragstart","SKIPOLE.widgets['" + widg_id + "'].dragstartfunc(event, '" + dragdata + "')");
                }
            else {
                $(this).attr("style",null);
                $(this).attr("draggable",null);
                $(this).attr("ondragstart",null);
                }
            });
        }
    if (droprows) {
        if (droprows.length != rows) {
            return;
            }
        tablerows.each(function( row ) {
            if (droprows[row][1]) {
                var dropdata = droprows[row][1];
                }
            else {
                var dropdata = "";
                }
            if (droprows[row][0]) {
                $(this).attr("ondrop","SKIPOLE.widgets['" + widg_id + "'].dropfunc(event, '" + dropdata + "')");
                $(this).attr("ondragover","SKIPOLE.widgets['" + widg_id + "'].allowdropfunc(event)");
                }
            else {
                $(this).attr("ondrop",null);
                $(this).attr("ondragover",null);
                }
            });
        }
    };


SKIPOLE.links.Audio1 = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    this.display_errors = false;
    };
SKIPOLE.links.Audio1.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.links.Audio1.prototype.constructor = SKIPOLE.links.Audio1;
SKIPOLE.links.Audio1.prototype.setvalues = function (fieldlist, result) {
    if (!this.widg_id) {
        return;
        }
    var the_widg = this.widg;
    var fieldvalues = this.fieldvalues;
    var play_audio = this.fieldarg_in_result("play", result, fieldlist);
    if (play_audio) {
        document.getElementById(this.widg_id).play();
        }
    };


SKIPOLE.links.Audio2 = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    this.display_errors = false;
    };
SKIPOLE.links.Audio2.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.links.Audio2.prototype.constructor = SKIPOLE.links.Audio2;
SKIPOLE.links.Audio2.prototype.setvalues = function (fieldlist, result) {
    if (!this.widg_id) {
        return;
        }
    var the_widg = this.widg;

    var src_mp3 = this.fieldarg_in_result("src_mp3", result, fieldlist);
    var src_wav = this.fieldarg_in_result("src_wav", result, fieldlist);
    var src_ogg = this.fieldarg_in_result("src_ogg", result, fieldlist);
    if (src_mp3 || src_wav || src_ogg) {
        // empty the widget audio src links
        the_widg.empty();
        var htmlcontent = "";
        if (src_mp3) {
            htmlcontent +=  "<source src=\"" + src_mp3 + "\" type=\"audio/mpeg\" />";
            }
        if (src_wav) {
            htmlcontent +=  "<source src=\"" + src_wav + "\" type=\"audio/wav\" />";
            }
        if (src_ogg) {
            htmlcontent +=  "<source src=\"" + src_ogg + "\" type=\"audio/ogg\" />";
            }
        the_widg.html(htmlcontent);
        document.getElementById(this.widg_id).load();
        }

    var play_audio = this.fieldarg_in_result("play", result, fieldlist);
    if (play_audio) {
        document.getElementById(this.widg_id).play();
        }
    };


