
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


import os, sys, pathlib

from datetime import datetime


SKIPOLE_AVAILABLE = True
try:
    from skipole import WSGIApplication, use_submit_list
    from skipole import skis
except:
    SKIPOLE_AVAILABLE = False

from indi_mr import tools

PROJECTFILES = os.path.dirname(os.path.realpath(__file__))
PROJECT = 'webdemo'


def _start_call(called_ident, skicall):
    "When a call is initially received this function is called."
    if called_ident is None:
        # blobs are served at /projectpath/blobs
        servedfile = skicall.map_url_to_server("blobs", skicall.proj_data["blob_folder"], "application/octet-stream")
        if servedfile:
            return servedfile
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


try:
    @use_submit_list
    def _submit_data(skicall):
        "This function is called when a Responder wishes to submit data for processing in some manner"
        return
except NameError:
    # if skipole is not imported @use_submit_list will flag a NameError 
    SKIPOLE_AVAILABLE = False


def _end_call(page_ident, page_type, skicall):
    """This function is called at the end of a call prior to filling the returned page with skicall.page_data"""
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
    


def make_wsgi_app(redisserver, blob_folder='', url="/"):
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
    if not SKIPOLE_AVAILABLE:
        return

    if blob_folder:
        blob_folder = pathlib.Path(blob_folder).expanduser().resolve()

    # The web service needs a redis connection, available in tools
    rconn = tools.open_redis(redisserver)
    proj_data = {"rconn":rconn, "redisserver":redisserver, "blob_folder":blob_folder}
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


