#!/home/indi/indienv/bin/python3


import redis

rconn = redis.Redis()


# getProperties

#values = ("", "", "")
#rconn.rpush("indi_:teststring", *values)
#rconn.publish("to_indi", "getProperties:teststring")

# getProperties

values = ("Telescope Simulator","ACTIVE_DEVICES","")
rconn.rpush("indi_:teststring2", *values)
rconn.publish("to_indi", "getProperties:teststring2")
