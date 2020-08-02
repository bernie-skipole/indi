

SKIPOLE.paras = {};


SKIPOLE.paras.TagBlock = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    this.display_errors = false;
    };
SKIPOLE.paras.TagBlock.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.paras.TagBlock.prototype.constructor = SKIPOLE.paras.TagBlock;
SKIPOLE.paras.TagBlock.prototype.dragstartfunc = function (e, data) {
    e.dataTransfer.setData("text/formname", this.formname('drag'));
    e.dataTransfer.setData("text/plain", data);
    };
SKIPOLE.paras.TagBlock.prototype.dropfunc = function (e, data) {
    e.preventDefault();
    var dragwidgfield = e.dataTransfer.getData("text/formname");
    var url = this.fieldvalues["dropurl"];
    if (!url) {
        return;
        }
    // now make a call, including data from the drag element and the drop element
    var dropwidgfield = this.formname('drop');
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
SKIPOLE.paras.TagBlock.prototype.allowdropfunc = function (e) {
     e.preventDefault();
    };

SKIPOLE.paras.TagBlock.prototype.setvalues = function (fieldlist, result) {
   if (!this.widg_id) {
        return;
        }
    var widg_id = this.widg_id
    var the_widg = this.widg;
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
    // enable or disable drag if a drag value is given
    var drag = this.fieldarg_in_result('drag', result, fieldlist);
    if (drag !== undefined) {
        if (drag) {
            the_widg.attr("draggable","true");
            the_widg.attr("ondragstart","SKIPOLE.widgets['" + widg_id + "'].dragstartfunc(event, '" + drag + "')");
            }
        else {
            the_widg.attr("draggable",null);
            the_widg.attr("ondragstart",null);
            }
        }
    // enable or disable drop if a drop value is given
    var drop = this.fieldarg_in_result('drop', result, fieldlist);
    if (drop !== undefined) {
        if (drop) {
            the_widg.attr("ondrop","SKIPOLE.widgets['" + widg_id + "'].dropfunc(event, '" + drop + "')");
            the_widg.attr("ondragover","SKIPOLE.widgets['" + widg_id + "'].allowdropfunc(event)");
            }
        else {
            the_widg.attr("ondrop",null);
            the_widg.attr("ondragover",null);
            }
        }
    };


SKIPOLE.paras.DivStyleDiv = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    this.display_errors = false;
    };
SKIPOLE.paras.DivStyleDiv.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.paras.DivStyleDiv.prototype.constructor = SKIPOLE.paras.DivStyleDiv;
SKIPOLE.paras.DivStyleDiv.prototype.setvalues = function (fieldlist, result) {
   if (!this.widg_id) {
        return;
        }
    var widg_id = this.widg_id
    var the_widg = this.widg;
    var set_html = this.fieldarg_in_result('set_html', result, fieldlist);
    if (set_html) {
        the_widg.html(set_html);
        }
    };


SKIPOLE.paras.DivHTML = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    this.display_errors = false;
    };
SKIPOLE.paras.DivHTML.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.paras.DivHTML.prototype.constructor = SKIPOLE.paras.DivHTML;
SKIPOLE.paras.DivHTML.prototype.dragstartfunc = function (e, data) {
    e.dataTransfer.setData("text/formname", this.formname('drag'));
    e.dataTransfer.setData("text/plain", data);
    };
SKIPOLE.paras.DivHTML.prototype.dropfunc = function (e, data) {
    e.preventDefault();
    var dragwidgfield = e.dataTransfer.getData("text/formname");
    var url = this.fieldvalues["dropurl"];
    if (!url) {
        return;
        }
    // now make a call, including data from the drag element and the drop element
    var dropwidgfield = this.formname('drop');
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
SKIPOLE.paras.DivHTML.prototype.allowdropfunc = function (e) {
     e.preventDefault();
    };

SKIPOLE.paras.DivHTML.prototype.setvalues = function (fieldlist, result) {
   if (!this.widg_id) {
        return;
        }
    var widg_id = this.widg_id
    var the_widg = this.widg;
    var set_html = this.fieldarg_in_result('set_html', result, fieldlist);
    if (set_html !== undefined) {
        the_widg.html(set_html);
        }
    // hide the widget
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
    // enable or disable drag if a drag value is given
    var drag = this.fieldarg_in_result('drag', result, fieldlist);
    if (drag !== undefined) {
        if (drag) {
            the_widg.attr("draggable","true");
            the_widg.attr("ondragstart","SKIPOLE.widgets['" + widg_id + "'].dragstartfunc(event, '" + drag + "')");
            }
        else {
            the_widg.attr("draggable",null);
            the_widg.attr("ondragstart",null);
            }
        }
    // enable or disable drop if a drop value is given
    var drop = this.fieldarg_in_result('drop', result, fieldlist);
    if (drop !== undefined) {
        if (drop) {
            the_widg.attr("ondrop","SKIPOLE.widgets['" + widg_id + "'].dropfunc(event, '" + drop + "')");
            the_widg.attr("ondragover","SKIPOLE.widgets['" + widg_id + "'].allowdropfunc(event)");
            }
        else {
            the_widg.attr("ondrop",null);
            the_widg.attr("ondragover",null);
            }
        }
    };


SKIPOLE.paras.SpanText = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    this.display_errors = false;
    };
SKIPOLE.paras.SpanText.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.paras.SpanText.prototype.constructor = SKIPOLE.paras.SpanText;
SKIPOLE.paras.SpanText.prototype.setvalues = function (fieldlist, result) {
    /* This widget accepts fields - span_text */
   if (!this.widg_id) {
        return;
        }
    var span_text = this.fieldarg_in_result('span_text', result, fieldlist);
    if (span_text !== undefined) {
        this.widg.text(span_text);
        }
    };


SKIPOLE.paras.TagText = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    this.display_errors = false;
    };
SKIPOLE.paras.TagText.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.paras.TagText.prototype.constructor = SKIPOLE.paras.TagText;
SKIPOLE.paras.TagText.prototype.setvalues = function (fieldlist, result) {
    /* This widget accepts fields - hide, tag_text */
   if (!this.widg_id) {
        return;
        }
    var the_widg = this.widg;
    /* tag_text */
    var tag_text = this.fieldarg_in_result('tag_text', result, fieldlist);
    if (tag_text !== undefined) {
        the_widg.text(tag_text);
        }
    /* hide */
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



SKIPOLE.paras.ParaText = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    this.display_errors = false;
    };
SKIPOLE.paras.ParaText.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.paras.ParaText.prototype.constructor = SKIPOLE.paras.ParaText;
SKIPOLE.paras.ParaText.prototype.setvalues = function (fieldlist, result) {
    /* This widget accepts fields - para_text */
   if (!this.widg_id) {
        return;
        }
    var para_text = this.fieldarg_in_result('para_text', result, fieldlist);
    if (para_text !== undefined) {
        this.widg.text(para_text);
        }
    };


SKIPOLE.paras.PreText = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    };
SKIPOLE.paras.PreText.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.paras.PreText.prototype.constructor = SKIPOLE.paras.PreText;
SKIPOLE.paras.PreText.prototype.setvalues = function (fieldlist, result) {
    if (!this.widg_id) {
        return;
        }
    /* check if an error message or clear_error is given */
    if (this.check_error(fieldlist, result)) {
        return;
        }
    // pre_text
    var pre_text = this.fieldarg_in_result('pre_text', result, fieldlist);
    if (pre_text !== undefined) {
        this.widg.text(pre_text);
        }
    };
SKIPOLE.paras.PreText.prototype.show_error = function (error_message) {
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
    };
SKIPOLE.paras.PreText.prototype.clear_error = function() {
    if (!this.widg_id) {
        return;
        }
    var the_widg = this.widg;
    if (the_widg.attr("data-status") == "error") {
        the_widg.removeAttr( "data-status" )
        }
    };


SKIPOLE.paras.DivPara = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    };
SKIPOLE.paras.DivPara.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.paras.DivPara.prototype.constructor = SKIPOLE.paras.DivPara;
SKIPOLE.paras.DivPara.prototype.setvalues = function (fieldlist, result) {
    /* This widget accepts fields - para_text */
   if (!this.widg_id) {
        return;
        }
    /* check if an error message or clear_error is given */
    if (this.check_error(fieldlist, result)) {
        return;
        }
    var para_text = this.fieldarg_in_result('para_text', result, fieldlist);
    if (para_text !== undefined) {
        var paragraph = this.widg.children().filter(":first");
        paragraph.text(para_text);
        }
    };
SKIPOLE.paras.DivPara.prototype.show_error = function (error_message) {
    /* sets data-status and ensures first child contains error_message and has class error_class  */
    if (!error_message) {
        error_message = this.error_message;
        }
    if (!error_message) {
        error_message = "Unknown Error";
        }
    var the_widg = this.widg;
    the_widg.attr("data-status", "error");
    var paragraph = the_widg.find(':first');
    paragraph.text(error_message);
    var error_class = this.fieldvalues["error_class"];
    if (error_class) {
        paragraph.attr("class", error_class);
        }
    };
SKIPOLE.paras.DivPara.prototype.clear_error = function() {
    if (!this.widg_id) {
        return;
        }
    var the_widg = this.widg;
    if (the_widg.attr("data-status") == "error") {
        the_widg.removeAttr( "data-status" );
        }
    var paragraph = the_widg.find(':first');
    paragraph.removeAttr( "class" );
    var para_class = this.fieldvalues["para_class"];
    if (para_class) {
        paragraph.attr("class", para_class);
        }
    };


SKIPOLE.paras.JSONTextLink = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    };
SKIPOLE.paras.JSONTextLink.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.paras.JSONTextLink.prototype.constructor = SKIPOLE.paras.JSONTextLink;
SKIPOLE.paras.JSONTextLink.prototype.clear_error = function () {
    if (!this.widg_id) {
        return;
        }
    var the_widg = this.widg;
    the_widg.removeAttr("data-status");
    var textbox = the_widg.children().filter(":last");
    var button_show_text = this.fieldvalues["button_show_text"];
    if (!button_show_text) {
        button_show_text = "Show";
        }
    if (textbox.is(":visible")) {
        textbox.fadeOut('slow');
        the_widg.children().filter(":first").text(button_show_text);
        }
    };
SKIPOLE.paras.JSONTextLink.prototype.show_error = function (error_message) {
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

    /* button_hide_text */
    var button_hide_text = this.fieldvalues["button_hide_text"];
    if (!button_hide_text) {
        button_hide_text = "Hide";
        }
    var textbox = the_widg.children().filter(":last");
    if (textbox.is(":visible")) {
        textbox.text(error_message);
        }
    else {
        /* not visible, so has to fade in, and button now shows hide text */
        textbox.text(error_message).fadeIn('slow');
        the_widg.children().filter(":first").text(button_hide_text);
        }
    };
SKIPOLE.paras.JSONTextLink.prototype.setvalues = function (fieldlist, result) {
    /* This widget accepts fields - show_error, hide and para_text */
    if (!this.widg_id) {
        return;
        }
    /* check if an error message or clear_error is given */
    if (this.check_error(fieldlist, result)) {
        return;
        }
    var para_text = this.fieldarg_in_result('para_text', result, fieldlist);
    var the_widg = this.widg;

    // get button_hide_text
    var button_hide_text = this.fieldvalues["button_hide_text"];
    if (!button_hide_text) {
        button_hide_text = "Hide";
        }
    // get button_show_text
    var button_show_text = this.fieldvalues["button_show_text"];
    if (!button_show_text) {
        button_show_text = "Show";
        }
    // para_text
    var textbox = the_widg.children().filter(":last");
    if (para_text !== undefined) {
        textbox.text(para_text);
        }
    // hide
    var hidebox = this.fieldarg_in_result('hide', result, fieldlist);
    if (hidebox != undefined) {
        if (hidebox) {
            if (textbox.is(":visible")) {
                textbox.fadeOut('slow');
                the_widg.children().filter(":first").text(button_show_text);
                }
            }
        else {
            if (!(textbox.is(":visible"))) {
                textbox.fadeIn('slow');
                the_widg.children().filter(":first").text(button_hide_text);
                }
            }
        }
    };
SKIPOLE.paras.JSONTextLink.prototype.eventfunc = function (e) {
    if (!this.widg_id) {
        return;
        }
    var fieldvalues = this.fieldvalues;
    if (!fieldvalues["url"]) {
        return;
        }
    var the_widg = this.widg;
    var button_show_text = fieldvalues["button_show_text"];
    if (!button_show_text) {
        button_show_text = "Show";
        }
    var textbox = the_widg.children().filter(":last");
    e.preventDefault();
    if (textbox.is(":visible")) {
        textbox.fadeOut('slow');
        $(e.target).text(button_show_text);
        }
    else {
        var href = $(e.target).attr('href');
        var senddata = href.substring(href.indexOf('?')+1);
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
        }

    };


SKIPOLE.paras.JSONDivLink = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    };
SKIPOLE.paras.JSONDivLink.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.paras.JSONDivLink.prototype.constructor = SKIPOLE.paras.JSONDivLink;
SKIPOLE.paras.JSONDivLink.prototype.clear_error = function () {
    if (!this.widg_id) {
        return;
        }
    var the_widg = this.widg;
    the_widg.removeAttr("data-status");
    var button_show_text = this.fieldvalues["button_show_text"];
    var divbox = the_widg.children().filter(":last");
    if (!button_show_text) {
        button_show_text = "Show";
        }
    if (divbox.is(":visible")) {
        divbox.fadeOut('slow');
        the_widg.children().filter(":first").text(button_show_text);
        }
    };
SKIPOLE.paras.JSONDivLink.prototype.show_error = function (error_message) {
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
    /* get text or html */
    var textorhtml = this.fieldvalues["htmlescaped"];
    if (!textorhtml) {
        textorhtml = "text";
        }
    var button_hide_text = this.fieldvalues["button_hide_text"];
    if (!button_hide_text) {
        button_hide_text = "Hide";
        }
    var divbox = the_widg.children().filter(":last");
    if (divbox.is(":visible")) {
        if (textorhtml == "html") {
            divbox.html(error_message);
            }
        else {
            divbox.text(error_message);
            }
        }
    else {
        /* not visible, so has to fade in, and button now shows hide text */
        if (textorhtml == "html") {
            divbox.html(error_message).fadeIn('slow');
            }
        else {
            divbox.text(error_message).fadeIn('slow');
            }
        the_widg.children().filter(":first").text(button_hide_text);
        }
    };
SKIPOLE.paras.JSONDivLink.prototype.setvalues = function (fieldlist, result) {
    /* This widget accepts fields - show_error, hide and para_text */
    if (!this.widg_id) {
        return;
        }
     /* check if an error message or clear_error is given */
    if (this.check_error(fieldlist, result)) {
        return;
        }
    var div_content = this.fieldarg_in_result('div_content', result, fieldlist);
    var the_widg = this.widg;
    // get text or html
    var textorhtml = this.fieldvalues["htmlescaped"];
    if (!textorhtml) {
        textorhtml = "text";
        }
    // get button_hide_text
    var button_hide_text = this.fieldvalues["button_hide_text"];
    if (!button_hide_text) {
        button_hide_text = "Hide";
        }
    // get button_show_text
    var button_show_text = this.fieldvalues["button_show_text"];
    if (!button_show_text) {
        button_show_text = "Show";
        }
    // div_content
    var divbox = the_widg.children().filter(":last");
    if (div_content) {
        if (textorhtml == "html") {
            divbox.html(div_content);
            }
        else {
            divbox.text(div_content);
            }
        }
    // hide
    var hidebox = this.fieldarg_in_result('hide', result, fieldlist);
    if (hidebox != undefined) {
        if (hidebox) {
            if (divbox.is(":visible")) {
                divbox.fadeOut('slow');
                the_widg.children().filter(":first").text(button_show_text);
                }
            }
        else {
            if (!(divbox.is(":visible"))) {
                divbox.fadeIn('slow');
                the_widg.children().filter(":first").text(button_hide_text);
                }
            }
        }
    };
SKIPOLE.paras.JSONDivLink.prototype.eventfunc = function (e) {
    if (!this.widg_id) {
        return;
        }
    var fieldvalues = this.fieldvalues;
    var button_show_text = fieldvalues["button_show_text"];
    if (!button_show_text) {
        button_show_text = "Show";
        }
    e.preventDefault();
    if ($("#" + fieldvalues["divident"]).is(":visible")) {
        $("#" + fieldvalues["divident"]).fadeOut('slow');
        $("#" + fieldvalues["buttonident"]).text(button_show_text);
        }
    else {
        var senddata = {"ident":SKIPOLE.identdata};
        if (fieldvalues["get_field"]) {
            senddata[this.formname("get_field")] = fieldvalues["get_field"];
            }
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
        }
    };



SKIPOLE.paras.TextBlockPara = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    };
SKIPOLE.paras.TextBlockPara.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.paras.TextBlockPara.prototype.constructor = SKIPOLE.paras.TextBlockPara;
SKIPOLE.paras.TextBlockPara.prototype.setvalues = function (fieldlist, result) {
    /* This widget accepts fields - text_replaceblock */
   if (!this.widg_id) {
        return;
        }
    /* check if an error message or clear_error is given */
    if (this.check_error(fieldlist, result)) {
        return;
        }
    var text_replaceblock = this.fieldarg_in_result('text_replaceblock', result, fieldlist);
    if (text_replaceblock) {
        var linebreaks = this.fieldvalues["linebreaks"];
        if (linebreaks) {
            text_replaceblock = SKIPOLE.textbr(text_replaceblock);
            this.widg.html(text_replaceblock);
            }
        else {
            this.widg.text(text_replaceblock);
            }
        }
    };
SKIPOLE.paras.TextBlockPara.prototype.show_error = function (error_message) {
    /* sets data-status and ensures widget contains error_message and has class error_class  */
    if (!error_message) {
        error_message = this.error_message;
        }
    if (!error_message) {
        error_message = "Unknown Error";
        }
    var the_widg = this.widg;
    the_widg.attr("data-status", "error");
    var linebreaks = this.fieldvalues["linebreaks"];
    if (linebreaks) {
        error_message = SKIPOLE.textbr(error_message);
        the_widg.html(error_message);
        }
    else {
        the_widg.text(error_message);
        }
    var error_class = this.fieldvalues["error_class"];
    if (error_class) {
        the_widg.attr("class", error_class);
        }
    };
SKIPOLE.paras.TextBlockPara.prototype.clear_error = function() {
    if (!this.widg_id) {
        return;
        }
    var the_widg = this.widg;
    if (the_widg.attr("data-status") == "error") {
        the_widg.removeAttr( "data-status" );
        }
    the_widg.removeAttr( "class" );
    var widget_class = this.fieldvalues["widget_class"];
    if (widget_class) {
        the_widg.attr("class", widget_class);
        }
    };


SKIPOLE.paras.TextBlockDiv = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    this.display_errors = false;
    };
SKIPOLE.paras.TextBlockDiv.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.paras.TextBlockDiv.prototype.constructor = SKIPOLE.paras.TextBlockDiv;
SKIPOLE.paras.TextBlockDiv.prototype.setvalues = function (fieldlist, result) {
    /* This widget accepts field - content_replaceblock */
   if (!this.widg_id) {
        return;
        }
    var content_replaceblock = this.fieldarg_in_result('content_replaceblock', result, fieldlist);
    if (content_replaceblock) {
        this.widg.html(content_replaceblock);
        }
    };



SKIPOLE.paras.ShowPara1 = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    };
SKIPOLE.paras.ShowPara1.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.paras.ShowPara1.prototype.constructor = SKIPOLE.paras.ShowPara1;
SKIPOLE.paras.ShowPara1.prototype.setvalues = function (fieldlist, result) {
    /* check if an error message or clear_error is given */
    this.check_error(fieldlist, result);
    var the_widg = this.widg;
    var paragraph = the_widg.children().filter(":first");
    var para_text = this.fieldarg_in_result('para_text', result, fieldlist);
    if (para_text !== undefined) {
        paragraph.text(para_text);
        }
    var show_para = this.fieldarg_in_result('show_para', result, fieldlist);
    if (show_para !== undefined) {
        if (show_para) {
            if (!(paragraph.is(":visible"))) {
                paragraph.fadeIn('slow');
                }
            }
        else {
            if (paragraph.is(":visible")) {
                paragraph.fadeOut('slow');
                }
            }
        }
    };
SKIPOLE.paras.ShowPara1.prototype.show_error = function (error_message) {
    if (!error_message) {
        error_message = this.error_message;
        }
    if (!error_message) {
        error_message = "Unknown Error";
        }
    var the_widg = this.widg;
    the_widg.attr("data-status", "error");
    var errordiv = the_widg.find("div:last");
    var paragraph = the_widg.find("p:last");
    paragraph.text(error_message);
    if (!(errordiv.is(":visible"))) {
        errordiv.fadeIn('slow');
        }
    };
SKIPOLE.paras.ShowPara1.prototype.clear_error = function() {
    if (!this.widg_id) {
        return;
        }
    var the_widg = this.widg;
    if (the_widg.attr("data-status") == "error") {
        the_widg.removeAttr( "data-status" )
        }
    var errordiv = the_widg.find("div:last");
    if (errordiv.is(":visible")) {
        errordiv.fadeOut('slow');
        }
    };


SKIPOLE.paras.ShowPara2 = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    this.display_errors = false;
    };
SKIPOLE.paras.ShowPara2.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.paras.ShowPara2.prototype.constructor = SKIPOLE.paras.ShowPara2;
SKIPOLE.paras.ShowPara2.prototype.setvalues = function (fieldlist, result) {
    var the_widg = this.widg;
    var paragraph = the_widg.find("p");
    var para_text = this.fieldarg_in_result('para_text', result, fieldlist);
    if (para_text !== undefined) {
        paragraph.text(para_text);
        }
    var hide = this.fieldarg_in_result('hide', result, fieldlist);
    if (hide !== undefined) {
        if (hide) {
            if (the_widg.is(":visible")) {
                the_widg.hide();
                }
            }
        else {
            if (!(the_widg.is(":visible"))) {
                the_widg.show();
                }
            }
        }
    };


