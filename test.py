#!/home/indi/indienv/bin/python3


import redis

rconn = redis.Redis()


rconn.publish("to_indi", "getProperties")

