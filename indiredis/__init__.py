
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


import os, sys, pathlib, time, configparser, hashlib, threading, json

from datetime import datetime

from waitress import serve

from skipole import WSGIApplication, use_submit_list, skis, ServeFile, set_debug

from indi_mr import tools, inditoredis, indi_server, redis_server, mqtttoredis, mqtt_server, driverstoredis

PROJECTFILES = os.path.dirname(os.path.realpath(__file__))
PROJECT = 'indiredis'


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
    if skicall.call_data.get('authenticate'):
        # a user has logged in, set a cookie
        return skicall.call_data['authenticate']
    if skicall.call_data.get('logout'):
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
    proj = skicall.proj_ident
    if proj not in skicall.received_cookies:
        return False
    receivedcookie = skicall.received_cookies[proj]
    # check cookie exists in redis sorted set
    rediskey = skicall.proj_data["rediskey"]
    rconn = skicall.proj_data["rconn"]
    # check the score of this cookie in the sorted set
    score = rconn.zscore(rediskey, receivedcookie)
    # if this cookie has a score of None, it does not exist
    if not score:
        return False
    # cookie exist, update its score - which is the unix timestamp
    rconn.zadd(rediskey, {receivedcookie:time.time()}, xx=True)
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
    :param hashedpassword: Hashed password or empty value
    :type hashedpassword: String
    :return: A WSGI callable application
    :rtype: skipole.WSGIApplication
    """

    if blob_folder:
        blob_folder = pathlib.Path(blob_folder).expanduser().resolve()

    # The web service needs a redis connection, available in tools
    rconn = tools.open_redis(redisserver)
    # and pass parameters in proj_data, note that resdiskey will be the key used to store cookies, created
    # as users log in
    proj_data = {"rconn":rconn,
                 "redisserver":redisserver,
                 "rediskey":redisserver.keyprefix + 'cookies',
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

    #set_debug(True)

    return application


# The function confighelper helps generate a config file which should look like:

#  [WEB]
#  # Set this to the folder where Blobs will be stored
#  blob_folder = path/to/blob/folder
#  # Set this to a hashed password string which will be required to access the
#  # web pages, or do not include this parameter if no password is required
#  hashedpassword = hash-of-password
#  # web service host and port
#  host = localhost
#  port = 8000
#
#  # only one of the following [INDI], [MQTT] or [DRIVERS] should
#  # be given. They are mutually exclusive.
#
#  [INDI]
#  # indi server host and port
#  ihost = localhost
#  iport = 7624
#
#  [MQTT]
#  # mqtt server host, port and client id
#  mhost = localhost
#  mport = 1883
#  mqtt_id = indi_client01
#  # mqtt topics
#  to_indi_topic = to_indi
#  from_indi_topic = from_indi
#  snoop_control_topic = snoop_control
#  snoop_data_topic = snoop_data
#
#  [MQTT.SUBSCRIBE_LIST]
#  # A list of remote mqtt_id's to subscribe to, for example
#  indi_drivers01
#  indi_drivers02
#
#  [DRIVERS]
#  # a list of drivers, for example
#  indi_simulator_telescope
#  indi_simulator_ccd
#
#  [REDIS]
#  # redis server host and port
#  rhost = localhost
#  rport = 6379
#  # Prefix applied to redis keys
#  prefix = indi_
#  # Redis channel used to publish data to indiserver
#  toindipub = to_indi
#  # Redis channel on which data is published from indiserver
#  fromindipub = from_indi



def confighelper(path):
    """This generates a config file and is normally run in the python REPL,
    path should be the path of the file you wish to make, and should not
    already exist. You will be asked a series of questions and then the
    file will be generated.

    :param path: path of the file to be generated
    :type path: String
    """

    hp = "localhost:8000"
    ihp = "localhost:7624"
    ihost = ""
    mhp = "localhost:1883"
    mhost = ""
    mqtt_id = "indi_client01"
    newmid = ""
    to_topic = 'to_indi'
    from_topic = 'from_indi'
    control_topic = 'snoop_control'
    data_topic = 'snoop_data'
    remote_ids = set()
    drivers = set()
    rhp = "localhost:6379"
    prefix = "indi_"
    toindipub = "to_indi"
    fromindipub = "from_indi"

    # the path should be to a directory which exits, but not an existing file

    configfile = os.path.abspath(os.path.expanduser(path))
    if os.path.exists(configfile):
        print(f"Error: {configfile} already exists!")
        sys.exit(1)

    configdir = os.path.dirname(configfile)
    if not os.path.isdir(configdir):
        print(f"Error: the directory {configdir} has not been found!")
        sys.exit(1)

    while True:
        print("Type in the host and port where the web service will be served,\nas colon separated host:number")
        newhp = input("Currently : " + hp + "\nEnter to accept, or input new value>")
        if not newhp:
            newhp = hp
        if ":" not in newhp:
            print("Invalid web host:port")
            continue
        try:
            host,port = newhp.split(":")
            port = int(port)
        except:
            print("Invalid web host:port")
            continue
        print("Value set at : " + newhp + "\n")
        q = input("OK (y/n)?")
        if q == "y" or q == "Y":
            break

    print("\nYou can specify one of the following three:")
    print("The host:port of an INDI server (which itself connects to instruments and drivers).")
    print("Or\nThe host:port of an MQTT server (which connect to instruments using the indi-mr package).")
    print("Or\nA list of indi drivers, which in turn connect to instruments.\n")
    q = input("Do you wish to connect to an INDI server (y/n)?")
    if q == "y" or q == "Y":
        while True:
            print("\nType in the host and port of the indi service to connect to,\nas colon separated host:number")
            newihp = input("Currently : " + ihp + "\nEnter to accept, or input new value>")
            if not newihp:
                newihp = ihp
            if ":" not in newihp:
                print("Invalid indi host:port")
                continue
            try:
                ihost,iport = newihp.split(":")
                iport = int(iport)
            except:
                print("Invalid indi host:port")
                continue
            print("Value set at : " + newihp + "\n")
            q = input("OK (y/n)?")
            if q == "y" or q == "Y":
                break
    else:
        # Not indi server, could be mqtt or drivers
        q = input("\nDo you wish to connect to an MQTT server (y/n)?")
        if q == "y" or q == "Y":
            while True:
                print("\nType in the host and port of the mqtt service to connect to,\nas colon separated host:number")
                newmhp = input("Currently : " + mhp + "\nEnter to accept, or input new value>")
                if not newmhp:
                    newmhp = mhp
                if ":" not in newmhp:
                    print("Invalid mqtt host:port")
                    continue
                try:
                    mhost,mport = newmhp.split(":")
                    mport = int(mport)
                except:
                    print("Invalid mqtt host:port")
                    continue
                print("Value set at : " + newmhp + "\n")
                q = input("OK (y/n)?")
                if q == "y" or q == "Y":
                    break
            while True:
                print("\nType in a string which will be the MQTT client ID.\nThis should be unique if there are multiple MQTT clients.")
                newmid = input("Currently : " + mqtt_id + "\nEnter to accept, or input new string>")
                if not newmid:
                    newmid = mqtt_id
                print("String set at : " + newmid + "\n")
                q = input("OK (y/n)?")
                if q == "y" or q == "Y":
                    break
            while True:
                print("\nType in a string which will be the MQTT topic communicating to drivers.")
                to_indi_topic = input("Currently : " + to_topic + "\nEnter to accept, or input new string>")
                if not to_indi_topic:
                    to_indi_topic = to_topic
                print("String set at : " + to_indi_topic + "\n")
                q = input("OK (y/n)?")
                if q == "y" or q == "Y":
                    break
            while True:
                print("\nType in a string which will be the MQTT topic communicating to the client.")
                from_indi_topic = input("Currently : " + from_topic + "\nEnter to accept, or input new string>")
                if not from_indi_topic:
                    from_indi_topic = from_topic
                print("String set at : " + from_indi_topic + "\n")
                q = input("OK (y/n)?")
                if q == "y" or q == "Y":
                    break
            while True:
                print("\nType in a string which will be the MQTT topic used for driver snoop control.")
                snoop_control_topic = input("Currently : " + control_topic + "\nEnter to accept, or input new string>")
                if not snoop_control_topic:
                    snoop_control_topic = control_topic
                print("String set at : " + snoop_control_topic + "\n")
                q = input("OK (y/n)?")
                if q == "y" or q == "Y":
                    break
            while True:
                print("\nType in a string which will be the MQTT topic used for driver snoop data.")
                snoop_data_topic = input("Currently : " + data_topic + "\nEnter to accept, or input new string>")
                if not snoop_data_topic:
                    snoop_data_topic = data_topic
                print("String set at : " + snoop_data_topic + "\n")
                q = input("OK (y/n)?")
                if q == "y" or q == "Y":
                    break
            print("/nDo you want to list the remote driver mqtt id's to which this client connects?")
            print("If not then the client will connect (subscribe) to all mqtt id's")
            q = input("List mqtt id's to subscribe to (y/n)?")
            if q == "y" or q == "Y":
                # fill section MQTT.SUBSCRIBE_LIST
                print("\nType an id string and Enter, you will then be prompted for the next id.")
                print("Continue adding id's, and then just press Enter without input to finish.")
                while True:
                    idstring = input("mqtt_id : ")
                    idstring = idstring.strip(" \"\'")
                    if not idstring:
                        break
                    remote_ids.add(dstring)
        else:
            # neither indi nor mqtt servers, therfore should be drivers
            q = input("\nDo you wish to define one or more drivers (y/n)?")
            if q != "y" and q != "Y":
                print("No other options are available. Exiting without creating config file")
                sys.exit(0)
            print("\nType a driver string and Enter, you will then be prompted for the next driver.")
            print("Continue adding drivers, and then just press Enter without input to finish.")
            while True:
                dstring = input("Driver : ")
                dstring = dstring.strip(" \"\'")
                if not dstring:
                    break
                drivers.add(dstring)
            if not drivers:
                print("No drivers specified, no other options are available. Exiting without creating config file")
                sys.exit(0)

    while True:
        print("\nType in the host and port of the redis service to connect to,\nas colon separated host:number")
        newrhp = input("Currently : " + rhp + "\nEnter to accept, or input new value>")
        if not newrhp:
            newrhp = rhp
        if ":" not in newrhp:
            print("Invalid redis host:port")
            continue
        try:
            rhost,rport = newrhp.split(":")
            rport = int(rport)
        except:
            print("Invalid redis host:port")
            continue
        print("Value set at : " + newrhp + "\n")
        q = input("OK (y/n)?")
        if q == "y" or q == "Y":
            break

    while True:
        print("\nType in a string which will be prefixed to the indi keys saved in redis.\nThis is used to avoid any other uses of redis you may have.")
        newprefix = input("Currently : " + prefix + "\nEnter to accept, or input new string>")
        if not newprefix:
            newprefix = prefix
        print("String set at : " + newprefix + "\n")
        q = input("OK (y/n)?")
        if q == "y" or q == "Y":
            break

    while True:
        print("\nType in a string which will be used as a redis publish channel when data is to be transmitted to the INDI service.")
        newtoindipub = input("Currently : " + toindipub + "\nEnter to accept, or input new string>")
        if not newtoindipub:
            newtoindipub = toindipub
        print("String set at : " + newtoindipub + "\n")
        q = input("OK (y/n)?")
        if q == "y" or q == "Y":
            break

    while True:
        print("\nType in a string which will be used as a redis publish channel when data is received from the INDI service.")
        newfromindipub = input("Currently : " + fromindipub + "\nEnter to accept, or input new string>")
        if not newfromindipub:
            newfromindipub = fromindipub
        print("String set at : " + newfromindipub + "\n")
        q = input("OK (y/n)?")
        if q == "y" or q == "Y":
            break

    while True:
        print("\nType in a path to the folder where Blobs will be stored.")
        blob_folder = input("input path>")
        if not blob_folder:
            continue
        blob_folder = os.path.abspath(os.path.expanduser(blob_folder))
        print("BLOB folder set at : " + blob_folder + "\n")
        q = input("OK (y/n)?")
        if q == "y" or q == "Y":
            break

    while True:
        print("\nEnter for no password, or type in a password which will be used to access the client.")
        password = input("input password>")
        if password:
            print("Password set at : " + password + "\n")
        else:
            print("No password set.\n")
        q = input("OK (y/n)?")
        if q == "y" or q == "Y":
            break

    print("\nAll parameters have been set, type y to save the config file, or any other character to exit without creating a file.")
    proceed = input("Create file (y/n)?>")
    if proceed != "y" and proceed != "Y":
        sys.exit(0)

    if password:
        hashedpassword = hashlib.sha512( password.encode('utf-8') ).hexdigest()
        hashedpasswordkey = 'hashedpassword'
    else:
        hashedpassword = None
        hashedpasswordkey = '# hashedpassword ='


    config = configparser.ConfigParser(allow_no_value=True)

    config['WEB'] =        { "# Set this to the folder where Blobs will be stored": None,
                             'blob_folder': blob_folder,
                             "# Set this to a hashed password string which will be required to access the": None,
                             "# web pages, or do not include this parameter if no password is required": None,
                             hashedpasswordkey: hashedpassword,
                             '# web service host and port': None,
                             'host': host,
                             'port': port
                           }

    if ihost:
        config['INDI'] =   { '# indi server host and port': None,
                             'ihost': ihost,
                             'iport': iport
                           }
    elif mhost:
        config['MQTT'] =   { '# mqtt server host, port and client id': None,
                             'mhost': mhost,
                             'mport': mport,
                             'mqtt_id': newmid,
                             '# mqtt topics': None,
                             'to_indi_topic': to_indi_topic,
                             'from_indi_topic': from_indi_topic,
                             'snoop_control_topic': snoop_control_topic,
                             'snoop_data_topic': snoop_data_topic
                           }
        if remote_ids:
            iddict = { "# A list of remote mqtt_id's to subscribe to, for example": None }
            for ids in remote_ids:
                iddict[ids] = None
            config['MQTT.SUBSCRIBE_LIST'] = iddict

    elif drivers:
        driverdict = { '# a list of drivers': None }
        for driver in drivers:
            driverdict[driver] = None
        config['DRIVERS'] = driverdict

    config['REDIS'] =      { '# redis server host and port': None,
                             'rhost': rhost,
                             'rport': rport,
                             '# Prefix applied to redis keys': None,
                             'prefix': newprefix,
                             '# Redis channel used to publish data to indiserver': None,
                             'toindipub': newtoindipub,
                             '# Redis channel on which data is published from indiserver': None,
                             'fromindipub': newfromindipub
                           }


    with open(configfile, 'w') as cf:
        config.write(cf)

    print(f"File {configfile} has been created")
    sys.exit(0)


def _read_config(configfile):
    "Reads the configfile and returns dictionary of parameters"
    config = configparser.ConfigParser(allow_no_value=True)
    config.read(configfile)
    configdict = {}
    if 'WEB' not in config:
        print("ERROR: The config file does not include a WEB section.")
        sys.exit(1)
    webparams = config['WEB']
    configdict['blob_folder'] = webparams['blob_folder']
    configdict['hashedpassword'] = webparams.get('hashedpassword', '')
    configdict['host'] = webparams.get('host', 'localhost')
    configdict['port'] = webparams.getint('port', 8000)
    if 'INDI' in config:
        indiparams = config['INDI']
        configdict['ihost'] = indiparams.get('ihost', 'localhost')
        configdict['iport'] = indiparams.getint('iport', 7624)
    elif 'MQTT' in config:
        mqttparams = config['MQTT']
        configdict['mhost'] = mqttparams.get('mhost', 'localhost')
        configdict['mport'] = mqttparams.getint('mport', 1883)
        configdict['mqtt_id'] = mqttparams.get('mqtt_id', 'indi_client01')
        configdict['to_indi_topic'] = mqttparams.get('to_indi_topic', 'to_indi')
        configdict['from_indi_topic'] = mqttparams.get('from_indi_topic', 'from_indi')
        configdict['snoop_control_topic'] = mqttparams.get('snoop_control_topic', 'snoop_control')
        configdict['snoop_data_topic'] = mqttparams.get('snoop_data_topic', 'snoop_data')
        if 'MQTT.SUBSCRIBE_LIST' in config:
            subscribe_list = config['MQTT.SUBSCRIBE_LIST']
            configdict['subscribe_list'] = list(subscribe_list.keys())
        else:
            configdict['subscribe_list'] = []
    elif 'DRIVERS' in config:
        drivers = config['DRIVERS']
        configdict['drivers'] = list(drivers.keys())
        if not configdict['drivers']:
            print("ERROR: No drivers given under DRIVERS.")
            sys.exit(1)
    else:
        print("ERROR: No INDI, MQTT or DRIVERS section in the config file.")
        sys.exit(1)
    if 'REDIS' not in config:
        print("ERROR: The config file does not include a REDIS section.")
        sys.exit(1)
    redisparams = config['REDIS']
    configdict['rhost'] = redisparams.get('rhost', 'localhost')
    configdict['rport'] = redisparams.getint('rport', 6379)
    configdict['prefix'] = redisparams.get('prefix', 'indi_')
    configdict['toindipub'] = redisparams.get('toindipub', 'to_indi')
    configdict['fromindipub'] = redisparams.get('fromindipub', 'from_indi')
    return configdict


def runclient(configfile):
    """Blocking call, which given the path to a config reads the
    parameters and runs the web client

    :param configfile: path to the config file
    :type configfile: String
    """

    configfile = os.path.abspath(os.path.expanduser(configfile))
    if not os.path.isfile(configfile):
        print("The configuration file has not been found")
        sys.exit(1)

    configdict = _read_config(configfile)

    redis_host = redis_server(host=configdict["rhost"], port=configdict["rport"],
                              db=0, password='',
                              keyprefix=configdict['prefix'],
                              to_indi_channel=configdict['toindipub'],
                              from_indi_channel=configdict['fromindipub'])

    # create a wsgi application
    application = make_wsgi_app(redis_host, configdict['blob_folder'], url='/', hashedpassword=configdict['hashedpassword'])

    # serve the application with the python waitress web server in another thread
    webapp = threading.Thread(target=serve, args=(application,), kwargs={'host':configdict['host'], 'port':configdict['port']})
    webapp.start()

    if "ihost" in configdict:
        indi_host = indi_server(host=configdict["ihost"], port=configdict["iport"])
        # start the blocking function inditoredis
        inditoredis(indi_host, redis_host, log_lengths={}, blob_folder=configdict['blob_folder'])
    elif "mhost" in configdict:
        mqtt_host = mqtt_server(host=configdict["mhost"], port=configdict["mport"],
                                to_indi_topic = configdict['to_indi_topic'],
                                from_indi_topic = configdict['from_indi_topic'],
                                snoop_control_topic = configdict['snoop_control_topic'],
                                snoop_data_topic = configdict['snoop_data_topic'] )
        # start the blocking function mqtttoredis
        mqtttoredis(configdict['mqtt_id'], mqtt_host, redis_host, subscribe_list=configdict['subscribe_list'], blob_folder=configdict['blob_folder'])
    elif "drivers" in configdict:
        # start the blocking function driverstoredis
        driverstoredis(configdict['drivers'], redis_host, blob_folder=configdict['blob_folder'])
