
import os, sys


from datetime import datetime

from skipole import WSGIApplication, use_submit_list

from skipole import skis

from .. import tools



PROJECTFILES = os.path.join(os.path.dirname(os.path.realpath(__file__)), "webdata")
PROJECT = 'webdemo'


def start_call(called_ident, skicall):
    "When a call is initially received this function is called."
    if skicall.ident_data:
        # if ident_data exists, it should be a timestamp and
        # optionally the device name and property group to be displayed
        # set these into skicall.call_data
        sessiondata = skicall.ident_data.split("/n")
        skicall.call_data["timestamp"] = sessiondata[0]
        device = sessiondata[1]
        if device:
            skicall.call_data["device"] = device
        group = sessiondata[2]
        if group:
            skicall.call_data["group"] = group
    return called_ident

@use_submit_list
def submit_data(skicall):
    "This function is called when a Responder wishes to submit data for processing in some manner"
    return


def end_call(page_ident, page_type, skicall):
    """This function is called at the end of a call prior to filling the returned page with skicall.page_data"""
    if "status" in skicall.call_data:
        # display a modal status message
        skicall.page_data["status", "para_text"] = skicall.call_data["status"]
        skicall.page_data["status", "hide"] = False

    # set timestamp, device and group into a string to be sent as ident_data
    if "timestamp" in skicall.call_data:
        identstring = skicall.call_data["timestamp"] + "/n"
    else:
        identstring = datetime.utcnow().isoformat(sep='T') + "/n"
    if "device" in skicall.call_data:
        identstring += skicall.call_data["device"] + "/n"
    else:
        identstring += "/n"
    if "group" in skicall.call_data:
        identstring += skicall.call_data["group"]
    # set this string to ident_data
    skicall.page_data['ident_data'] = identstring
    


def make_wsgi_app(redis_host):
    """create the wsgi application"""
    # The web service needs a redis connection, available in tools
    rconn = tools.open_redis(redis_host)
    proj_data = {"rconn":rconn, "redisserver":redis_host}
    application = WSGIApplication(project=PROJECT,
                                  projectfiles=PROJECTFILES,
                                  proj_data=proj_data,
                                  start_call=start_call,
                                  submit_data=submit_data,
                                  end_call=end_call,
                                  url="/")

    skis_application = skis.makeapp(PROJECTFILES)
    application.add_project(skis_application, url='/lib')
    return application



######## add skiadmin during development
from skipole import skiadmin, set_debug

def add_skiadmin(application):
    set_debug(True)
    skiadmin_application = skiadmin.makeapp(PROJECTFILES, editedprojname=PROJECT)
    application.add_project(skiadmin_application, url='/skiadmin')
    return application



