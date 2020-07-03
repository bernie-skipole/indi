#!/home/indi/indienv/bin/python3


import redis

rconn = redis.Redis()


# getProperties

rconn.rpush("to_indi:teststring", ("","",""))
rconn.publish("to_indi", "getProperties:teststring")

# getProperties

rconn.rpush("to_indi:teststring2", ("Telescope Simulator","ACTIVE_DEVICES",""))
rconn.publish("to_indi", "getProperties:teststring2")
