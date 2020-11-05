
"""The main aim of indiredis is to provide redis storage for instrument parameters reported via the INDI protocol.
This makes it possible for a GUI that interfaces to redis to be written.

This module provides a WSGI web application as an example of such a GUI. This can be run by a wsgi complient web server.
""" 


import os, sys, pathlib

from datetime import datetime


SKIPOLE_AVAILABLE = True
try:
    from skipole import WSGIApplication, use_submit_list
    from skipole import skis
except:
    SKIPOLE_AVAILABLE = False

from .. import tools

PROJECTFILES = os.path.dirname(os.path.realpath(__file__))
PROJECT = 'webdemo'


def start_call(called_ident, skicall):
    "When a call is initially received this function is called."
    if called_ident is None:
        # Return None = url not found, if no called_ident, except if getting a file from blobs
        if skicall.path.startswith("/blobs/"):
            path = pathlib.Path(skicall.path)
            # there should be three elements / blobs and filename
            if len(path.parts) != 3:
                return
            skicall.page_data['mimetype'] = "application/octet-stream"
            blob_folder = skicall.proj_data["blob_folder"]
            if not blob_folder:
                return
            # blob_folder is a pathlib.Path object, returning this serves the file from the blob_folder
            return blob_folder / path.name
        return

    if skicall.ident_data:
        # if ident_data exists, it should be a timestamp and
        # optionally the device name and property group to be displayed
        # set these into skicall.call_data
        sessiondata = skicall.ident_data.split("/n")
        skicall.call_data["timestamp"] = sessiondata[0]
        changedata = sessiondata[1]
        if changedata:
            skicall.call_data["changedata"] = int(changedata)
        device = sessiondata[2]
        if device:
            skicall.call_data["device"] = device
        group = sessiondata[3]
        if group:
            skicall.call_data["group"] = group
    return called_ident


try:
    @use_submit_list
    def submit_data(skicall):
        "This function is called when a Responder wishes to submit data for processing in some manner"
        return
except NameError:
    # if skipole is not imported @use_submit_list will flag a NameError 
    SKIPOLE_AVAILABLE = False


def end_call(page_ident, page_type, skicall):
    """This function is called at the end of a call prior to filling the returned page with skicall.page_data"""
    if "status" in skicall.call_data:
        # display a modal status message
        skicall.page_data["status", "para_text"] = skicall.call_data["status"]
        skicall.page_data["status", "hide"] = False

    # set changedata, timestamp, device and group into a string to be sent as ident_data
    if "timestamp" in skicall.call_data:
        identstring = skicall.call_data["timestamp"] + "/n"
    else:
        identstring = datetime.utcnow().isoformat(sep='T') + "/n"
    # changedata is a checksum of the data shown on the page (using zlib.adler32(data))
    if 'changedata' in skicall.call_data:
        identstring += str(skicall.call_data['changedata']) + "/n"
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
    Reads and writes to redis stores created by indittoredis

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
                                  start_call=start_call,
                                  submit_data=submit_data,
                                  end_call=end_call,
                                  url=url)

    if url.endswith("/"):
        skisurl = url + "lib"
    else:
        skisurl = url + "/lib"

    skis_application = skis.makeapp()
    application.add_project(skis_application, url=skisurl)
    return application


