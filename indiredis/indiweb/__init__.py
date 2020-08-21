
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
        # if ident_data exists, it should be a timestamp and the device name
        # set these into skicall.call_data["device"] and skicall.call_data["timestamp"]
        splitdata = skicall.ident_data.split(" ", maxsplit=1)
        if len(splitdata) == 1:
            skicall.call_data["timestamp"] = splitdata[0]
        elif len(splitdata) == 2:
            timestamp, device = skicall.ident_data.split(" ", maxsplit=1)
            skicall.call_data["timestamp"] = timestamp
            skicall.call_data["device"] = device
    return called_ident

@use_submit_list
def submit_data(skicall):
    "This function is called when a Responder wishes to submit data for processing in some manner"
    return


def end_call(page_ident, page_type, skicall):
    """This function is called at the end of a call prior to filling the returned page with skicall.page_data,
       it can also return an optional session cookie string."""
    if "status" in skicall.call_data:
        # display a modal status message
        skicall.page_data["status", "para_text"] = skicall.call_data["status"]
        skicall.page_data["status", "hide"] = False
    # set timestamp and device to ident_data
    if "timestamp" in skicall.call_data:
        timestamp = skicall.call_data["timestamp"]
    else:
        timestamp = datetime.utcnow().isoformat(sep='T')
    if "device" in skicall.call_data:
        skicall.page_data['ident_data'] = timestamp + " " + skicall.call_data["device"]
    else:
        skicall.page_data['ident_data'] = timestamp


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



