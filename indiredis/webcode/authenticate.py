
import hashlib, uuid, time

from skipole import FailPage

# this is the maximum number of cookies generated, ie of simultaneous connections
N = 10


def login(skicall):
    "This function is called to checklogin from the login page"
    if ("password1", "input_text") in skicall.call_data:
        password = skicall.call_data["password1", "input_text"]
        hashed = hashlib.sha512( password.encode('utf-8')  ).hexdigest()
        if hashed == skicall.proj_data["hashedpassword"]:
            skicall.call_data['authenticate'] = _create_cookie(skicall)
            return
    raise FailPage("Invalid input")
            
            
def logout(skicall):
    "this call is to log out"
    skicall.call_data['logout'] = True
    proj = skicall.proj_ident
    receivedcookie = skicall.received_cookies[proj]
    # remove cookie from redis
    rediskey = skicall.proj_data["rediskey"]
    rconn = skicall.proj_data["rconn"]
    rconn.zrem(rediskey, receivedcookie)
    
    
def _create_cookie(skicall):
    "Generates a random cookie, store it in redis, and return the cookie"
    rediskey = skicall.proj_data["rediskey"]
    rconn = skicall.proj_data["rconn"]
    # generate a cookie string
    cookiestring = uuid.uuid4().hex
    rconn.zadd(rediskey, {cookiestring:time.time()}, nx=True)
    # Limit the number of cookies
    number = rconn.zcard(rediskey)
    if number > N:
        # delete the lowest score (oldest cookies)
        rconn.zremrangebyrank(rediskey, 0, -1*N)
    return cookiestring
