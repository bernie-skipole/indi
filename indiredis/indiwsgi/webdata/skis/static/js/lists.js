

SKIPOLE.lists = {};

SKIPOLE.lists.UList1 = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    this.display_errors = false;
    };
SKIPOLE.lists.UList1.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.lists.UList1.prototype.constructor = SKIPOLE.lists.UList1;
SKIPOLE.lists.UList1.prototype.setvalues = function (fieldlist, result) {
    if (!this.widg_id) {
        return;
        }
    var the_widg = this.widg;
    var fieldvalues = this.fieldvalues;
    // contents
    var contents = this.fieldarg_in_result('contents', result, fieldlist);
    // the class of the elements
    var even_class = fieldvalues["even_class"];
    var odd_class = fieldvalues["odd_class"];

    if (contents) {
        // If a request to renew the list is recieved, this block
        // empties the existing list, and re-draws it
        var rows = contents.length;
        // empty the list
        the_widg.empty();
        // and now start filling it again
        var htmlcontent = "";
        for (row = 0; row < rows; row++) {
            // for each row
            if (even_class && (row % 2)) {
                htmlcontent += "<li class = \"" + even_class + "\">";
                }
            else if (odd_class && (!(row % 2))) {
                htmlcontent += "<li class = \"" + odd_class + "\">";
                }
            else {
                htmlcontent += "<li>";
                }
            htmlcontent += SKIPOLE.textbr(contents[row]);
            // close the cell
            htmlcontent += "</li>";
            }
        the_widg.html(htmlcontent);
        }
    };



SKIPOLE.lists.UList2 = function (widg_id, error_message, fieldmap) {
    SKIPOLE.BaseWidget.call(this, widg_id, error_message, fieldmap);
    this.display_errors = false;
    };
SKIPOLE.lists.UList2.prototype = Object.create(SKIPOLE.BaseWidget.prototype);
SKIPOLE.lists.UList2.prototype.constructor = SKIPOLE.lists.UList2;
SKIPOLE.lists.UList2.prototype.setvalues = function (fieldlist, result) {
    if (!this.widg_id) {
        return;
        }
    var the_widg = this.widg;
    var fieldvalues = this.fieldvalues;
    // contents
    var contents = this.fieldarg_in_result('set_html', result, fieldlist);
    // the class of the elements
    var even_class = fieldvalues["even_class"];
    var odd_class = fieldvalues["odd_class"];

    if (contents) {
        // If a request to renew the list is recieved, this block
        // empties the existing list, and re-draws it
        var rows = contents.length;
        // empty the list
        the_widg.empty();
        // and now start filling it again
        var htmlcontent = "";
        for (row = 0; row < rows; row++) {
            // for each row
            if (even_class && (row % 2)) {
                htmlcontent += "<li class = \"" + even_class + "\">";
                }
            else if (odd_class && (!(row % 2))) {
                htmlcontent += "<li class = \"" + odd_class + "\">";
                }
            else {
                htmlcontent += "<li>";
                }
            htmlcontent += contents[row];
            // close the cell
            htmlcontent += "</li>";
            }
        the_widg.html(htmlcontent);
        }
    };


