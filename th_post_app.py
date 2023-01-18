# th_post_app.py  1-5-23  1330
#  https://www.youtube.com/watch?v=mSiqZRpgrfY  sqlite3-html
# all communications with th_ sensors 
# receives dict{} UDP byte strings with dict["name"] as identifier

import os
import sys
import time as tim
import json
import lems_time as lt
from baconfig3 import *

import requests

import socket

myname = socket.gethostname()

class gl:
    hostname = myname
    log_url = log_url = "%s:54300" % myname



def con_log(strng):  # now only startup, th_json, and errors logged 
    tim.sleep(0.1)
    print(strng)
'''   
    fname = "thpost.log"
    log_file = open(fname,"a")     # open or create and append to end 
    log_file.write(strng + "-" + lt.rtod(tim.time()) + "\n\n") # line per record with blank line seperator
    log_file.close()
    return()  
''' 

# -------------------------- post_log ------------------

def post_log(s1,s2):  # makes json of two strings then post_json
    log_dict = {"name" : s1,"jstrng" : s2}
    try:
        x = requests.post(gl.log_url, json = log_dict)
    except:
        con_log("41 requests post_log(%s,(%s , %s)) failed" % (gl.log_url,s1,s2) )

# ---------- post_json - goes to gl.log_url  same as post_log-----------------

def post_json(dict): # post a json dict

    try:
        x = requests.post(gl.log_url, json = dict)
        con_log("post_json(%s)" % json.dumps(dict))
    except:
        strng = ("51 requests.post(%s {%s}) failed" % (gl.log_url,json.dumps(dict)))
        con_log(strng)

num_argv = len(sys.argv)
if (num_argv > 1):   # 1 is 1 or 2 only
    a1 = sys.argv[1]
    if (a1 == "1"):
        gc.unit = gc.unit1
        gc.th_info["room"] = gc.room1

    elif (a1 == "2"):
        gc.unit = gc.unit2
        gc.th_info["room"] = gc.room2

    else:
        print("error sys.argv[1] =",a1) 
        sys.exit(1)

if (num_argv > 2):

    gl.hostname = sys.argv[2]

gl.log_url = "http://%s:54300/post_log/" % gl.hostname # "gl.hostname" # set to argv[1] or myname
print(gc.th_info["room"])

print(" gl.log_url=(%s)" % gl.log_url)


