/*

A javascript client-side validator is defined here for each of the python
server-side validators in module basic.py.  These javascript validators
are designed to support the server side validators, and improve the user
experience, but are not necessarily as rigorous.  Anything getting past
these, will then be tested by the server-side validators.

Call a validator function using
result = SKIPOLE.basic.testname(item, allowed_values, args);

Where testname is the python validator class name

item: is the input string being tested

allowed_values: an array of allowed strings

args: an object of further parameters depending on the validator

The function returns true if the test passes and is validated, false otherwise.

*/


SKIPOLE.basic = {
    /* Fail if no allowed values given, otherwise item must be in allowed values */
    'AllowedValuesOnly': function (item, allowed_values, args) {
        return SKIPOLE.inallowedlist(item, allowed_values);
        },
    /* ok if item is empty, otherwise item must be in allowed values */
    'AllowedValuesOrEmpty': function (item, allowed_values, args) {
        if (item === '') {
            return true;
            }
        return SKIPOLE.inallowedlist(item, allowed_values);
        },
    /* Aways passes */
    'NoOperation': function (item, allowed_values, args) {
        return true;
        },
    /* ok if item in allowed values, otherwise item must have length greater or equal to minlength */
    'MinLength': function (item, allowed_values, args) {
        if (SKIPOLE.inallowedlist(item, allowed_values)) {
            return true;
            }
        if (item.length < args.minlength) {
            return false;
            }
        return true;
        },
    /* ok if item in allowed values, otherwise item must have length less than or equal to maxlength */
    'MaxLength': function (item, allowed_values, args) {
        if (SKIPOLE.inallowedlist(item, allowed_values)) {
            return true;
            }
        if (item.length > args.maxlength) {
            return false;
            }
        return true;
        },
    /* item must not be empty */
    'NotEmpty': function (item, allowed_values, args) {
        if (item === false) {
            return true;
            }
        if (item === 0) {
            return true;
            }
        if (item === '0') {
            return true;
            }
        if (item) {
            return true;
            }
        return false;
        },
    /* ok if item is an integer string and between or equal to minval - maxval*/
    'IntMinMax': function (item, allowed_values, args) {
        if (SKIPOLE.inallowedlist(item, allowed_values)) {
            return true;
            }
        var reg = /^0-9/;
        if ( reg.test(item)) {
            return false;
            }
        /* item is an integer string */
        var value = parseInt(item, 10);
        if (value < args.minval) {
            return false;
            }
        if (value > args.maxval) {
            return false;
            }
        return true;
        },
    /* ok if item alphanumerical or underscore */
    'AlphaNumUnder': function (item, allowed_values, args) {
        if (SKIPOLE.inallowedlist(item, allowed_values)) {
            return true;
            }
        var reg = /[^\w]/;
        if (reg.test(item)) {
            return false;
            }
        return true;
    },
    /* ok if item alphanumerical, dot or underscore */
    'AlphaNumDotUnder': function (item, allowed_values, args) {
        if (SKIPOLE.inallowedlist(item, allowed_values)) {
            return true;
            }
        var reg = /[^\w\.]/;
        if (reg.test(item)) {
            return false;
            }
        return true;
    },
    /* ok if item matches the pattern */
    'Search': function (item, allowed_values, args) {
        if (SKIPOLE.inallowedlist(item, allowed_values)) {
            return true;
            }
        var reg = new RegExp(args.pattern, "i");
        if (reg.test(item)) {
            return true;
            }
        return false;
    }
};

