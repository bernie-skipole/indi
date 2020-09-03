/*

A javascript client-side validator is defined here for each of the python
server-side validators in module paths.py.  These javascript validators
are designed to support the server side validators, and improve the user
experience, but are not necessarily as rigorous.  Anything getting past
these, will then be tested by the server-side validators.

Call a validator function using
result = SKIPOLE.paths.testname(item, allowed_values, args);

Where testname is the python validator class name

item: is the input string being tested

allowed_values: an array of allowed strings

args: an object of further parameters depending on the validator

The function returns true if the test passes and is validated, false otherwise.

*/


SKIPOLE.paths = {
    /* Fail if no allowed values given, otherwise item must be in allowed values */

    /* no op */
    PathLeadingTrailingSlashes: function (item, allowed_values, args) {
        return true;
    },
    /* no op */
    IdentExists: function (item, allowed_values, args) {
        return true;
    },
    /* no op */
    NameNotInFolder: function (item, allowed_values, args) {
        return true;
    }
}



