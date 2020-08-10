
import os, sys

############ these lines for development mode ###########
skipole_package_location = "/home/bernard/git/skipole"

if skipole_package_location not in sys.path:
    sys.path.insert(0,skipole_package_location)
#########################################################

from skipole import WSGIApplication, FailPage, GoTo, ValidateError, ServerError, use_submit_list

from skipole import skis


from indiredis import redis_server, tools


redisserver = redis_server(host='localhost', port=6379, db=0, password='', keyprefix='indi_',
                          to_indi_channel='to_indi', from_indi_channel='from_indi')
# create redis connection

rconn = tools.open_redis(redisserver)

####### indiserver -v indi_simulator_telescope


proj_data = {'rconn':rconn,
             'redisserver':redisserver}

PROJECTFILES = os.path.join(os.path.dirname(os.path.realpath(__file__)), "webdata")
PROJECT = 'webdemo'


def start_call(called_ident, skicall):
    "When a call is initially received this function is called."
    return called_ident

@use_submit_list
def submit_data(skicall):
    "This function is called when a Responder wishes to submit data for processing in some manner"
    return


def end_call(page_ident, page_type, skicall):
    """This function is called at the end of a call prior to filling the returned page with skicall.page_data,
       it can also return an optional session cookie string."""
    return


# create the wsgi application
application = WSGIApplication(project=PROJECT,
                              projectfiles=PROJECTFILES,
                              proj_data=proj_data,
                              start_call=start_call,
                              submit_data=submit_data,
                              end_call=end_call,
                              url="/")



skis_application = skis.makeapp(PROJECTFILES)
application.add_project(skis_application, url='/lib')



if __name__ == "__main__":

    from skipole import skiadmin, skilift, set_debug

    skiadmin_application = skiadmin.makeapp(PROJECTFILES, editedprojname=PROJECT)
    application.add_project(skiadmin_application, url='/skiadmin')

    set_debug(True)

    # serve the application with the development server from skilift

    host = "127.0.0.1"
    port = 8000
    print("Serving %s on port %s. Call http://localhost:%s/skiadmin to edit." % (PROJECT, port, port))
    skilift.development_server(host, port, application)


