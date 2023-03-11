
"""
This package provides a WSGI web application. This can be run by a wsgi complient web server.

The package is highly dependent on the indi-mr package, which includes functions to
convert XML data received from indiserver to values stored in redis.

Running indiredis with the python3 -m option, imports and runs the indi-mr function
inditoredis, and creates a wsgi web application with the function make_wsgi_app().

Finally it serves the web application with the Python waitress web server.

Instead of running this indiredis package, you could import it, and then run
make_wsgi_app() in your own script with your preferred web server.
""" 


import os, pathlib

from datetime import datetime

from skipole import WSGIApplication, use_submit_list, skis, ServeFile, set_debug

from indi_mr import tools

PROJECTFILES = os.path.dirname(os.path.realpath(__file__))
PROJECT = 'indiredis'

set_debug(True)

def _start_call(called_ident, skicall):
    "When a call is initially received this function is called."

    if skicall.proj_data["hashedpassword"]:
        # a password has been set, so pages must be protected
        if _is_user_logged_in(skicall):
            # The user is logged in, so do not show the checklogin page
            if called_ident == (PROJECT, 17):
                # instead jump to home page
                return "home"
        else:
            # the user is not logged in, only allow the css page and checklogin page
            if (called_ident == (PROJECT, 1008)) or (called_ident == (PROJECT, 17)):
                return called_ident
            # any other page divert to login page
            return "login"

    if called_ident is None:
        # blobs are served at /projectpath/blobs
        servedfile = skicall.map_url_to_server("blobs", skicall.proj_data["blob_folder"])
        if servedfile:
            raise ServeFile(servedfile, mimetype="application/octet-stream")
        return

    if skicall.ident_data:
        # if ident_data exists, it should optionally be
        # the device name and property group to be displayed
        # with two checksums
        # checksum1 - flags if the page has been changed
        # checksum2 - flags if an html refresh is needed, rather than json update
        # set these into skicall.call_data
        sessiondata = skicall.ident_data.split("/n")
        checksum1 = sessiondata[0]
        if checksum1:
            skicall.call_data["checksum1"] = int(checksum1)
        checksum2 = sessiondata[1]
        if checksum2:
            skicall.call_data["checksum2"] = int(checksum2)
        device = sessiondata[2]
        if device:
            skicall.call_data["device"] = device
        group = sessiondata[3]
        if group:
            skicall.call_data["group"] = group
    return called_ident


@use_submit_list
def _submit_data(skicall):
    "This function is called when a Responder wishes to submit data for processing in some manner"
    return


def _end_call(page_ident, page_type, skicall):
    """This function is called at the end of a call prior to filling the returned page with skicall.page_data"""
    if ('authenticate' in skicall.call_data) and skicall.call_data['authenticate']:
        # a user has logged in, set a cookie
        return skicall.call_data['authenticate']
    if ('logout' in skicall.call_data) and skicall.call_data['logout']:
        # a user has been logged out, set an invalid cookie in the client
        return "xxxxxxxx"
        
    if "status" in skicall.call_data:
        # display a modal status message
        skicall.page_data["status", "para_text"] = skicall.call_data["status"]
        skicall.page_data["status", "hide"] = False

    # set device and group into a string to be sent as ident_data
        # with two checksums
        # checksum1 - flags if the page has been changed
        # checksum2 - flags if an html refresh is needed, rather than json update
    # checksum1 is a checksum of the data shown on the page (using zlib.adler32(data))
    if 'checksum1' in skicall.call_data:
        identstring = str(skicall.call_data['checksum1']) + "/n"
    else:
        identstring = "/n"
    if 'checksum2' in skicall.call_data:
        identstring += str(skicall.call_data['checksum2']) + "/n"
    else:
        identstring += "/n"
    if "device" in skicall.call_data:
        identstring += skicall.call_data["device"] + "/n"
    else:
        identstring += "/n"
    if "group" in skicall.call_data:
        identstring += skicall.call_data["group"]

    # set this string to ident_data
    skicall.page_data['ident_data'] = identstring


def _is_user_logged_in(skicall):
    "Checks if user is logged in"
    if PROJECT not in skicall.received_cookies:
        return False
    # get cookie
    rediskey = skicall.proj_data["redisserver"].keyprefix + 'cookiestring'
    rconn = skicall.proj_data["rconn"]
    cookievalue = rconn.get(rediskey)
    if not cookievalue:
        return False
    cookiestring = cookievalue.decode('utf-8')
    if skicall.received_cookies[PROJECT] != cookiestring:
        return False
    return True
    


def make_wsgi_app(redisserver, blob_folder='', url="/", hashedpassword=""):
    """Create a wsgi application which can be served by a WSGI compatable web server.
    Reads and writes to redis stores created by indi-mr

    :param redisserver: Named Tuple providing the redis server parameters
    :type redisserver: namedtuple
    :param blob_folder: Folder where Blobs will be stored
    :type blob_folder: String
    :param url: URL at which the web service is served
    :type url: String
    :return: A WSGI callable application
    :rtype: skipole.WSGIApplication
    """

    if blob_folder:
        blob_folder = pathlib.Path(blob_folder).expanduser().resolve()
        
    if not hashedpassword:
        hashedpassword = 'b109f3bbbc244eb82441917ed06d618b9008dd09b3befd1b5e07394c706a8bb980b1d7785e5976ec049b46df5f1326af5a2ea6d103fd07c95385ffab0cacbc86'

    # The web service needs a redis connection, available in tools
    rconn = tools.open_redis(redisserver)
    proj_data = {"rconn":rconn,
                 "redisserver":redisserver,
                 "blob_folder":blob_folder,
                 "hashedpassword":hashedpassword
                }
    application = WSGIApplication(project=PROJECT,
                                  projectfiles=PROJECTFILES,
                                  proj_data=proj_data,
                                  start_call=_start_call,
                                  submit_data=_submit_data,
                                  end_call=_end_call,
                                  url=url)

    if url.endswith("/"):
        skisurl = url + "lib"
    else:
        skisurl = url + "/lib"

    skis_application = skis.makeapp()
    application.add_project(skis_application, url=skisurl)

    return application


