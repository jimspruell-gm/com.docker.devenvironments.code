# baconfig.py 1-5-22 1947
# log cabin north hvac =bauto 192.168.195.75  user lc pw= LogC--- 
# [fe80::ba27:ebff:fe0b:eb0b:5620%12]
import json
import os
import sys
import time as tim

import lems_time as lt
import socket

myname=socket.gethostname()

class fl:  # filter
    tmp =  [[0.0,0.0,0.0,0.0,0.0],[0.0,0.0,0.0,0.0,0.0],\
            [0.0,0.0,0.0,0.0,0.0],[0.0,0.0,0.0,0.0,0.0],\
            [0.0,0.0,0.0,0.0,0.0],[0.0,0.0,0.0,0.0,0.0],\
            [0.0,0.0,0.0,0.0,0.0],[0.0,0.0,0.0,0.0,0.0]] # 1-7 rnum, 5 temps each
    ucnt = [0,0,0,0,0,0,0,0]  # counts for 1-7 units

class gc:
    hostname = myname
    post_time = 0.0

    dbug = 0 # display erceived records (th_json, ERROR, ...)
    dsp = 1  # display th_list[]
    terrcnt = 0
    error_count = 0
    count= [0,0,0,0,0,0,0,0] 
    secold= [0,0,0,0,0,0,0,0]
    cnt = 0
    chg = 0 
    log_url = "http://%s:54300/post_log/" % "localhost"
    #rnum          1        2      3       4       5       6        7     
    room2 = ["","1-FamRm","2-Kitch","3-BedRm","4-Basmt","5-2nd_Fl","6-StoRm","7-Outdr"]
    room1 = ["","Cabin","Basmt","RstRm","Kitch","Archv","Attic","OutDr"]

    unit2 = ["", "A430", "C30B", "AFF6","097D", "CC87", "9201", "99A1"]
    unit1 = ["", "19A0", "D821", "1CB0","4298", "7E88", "8FBF", "23EC"]

    
    last_update = 0  # if no chg update every 30 seconds (min 2,880/24 hrs)
#    num_units = 7
    totalcnt = 0
#  "rnum" : [0,   1,     2,      3,      4,      5,      6,       7],        
    unit = ["", "A430","C30B", "AFF6", "097D", "CC87", "9201", "99A1"]
    
    rssi = [0,-62,-62,-62,-62,-62,-62,-62]
    lstrng = ""  # last string
    strngchg = 0     # string chg
    dsp_rec={"name" : "dsp_rec",
       "strng" : ["","","","","","","","",""],
       "rtod" : ["","","","","","","",""] 
    }

    th_info={"name" : "th_info","errors" : 0,"room" : \
    ["","1-FamRoom","2-Kitchen","3-BedRoom","4-Basement","5-2nd_Floor","6-StorageRoom","7-Outside"],\
        "temp" :  [0,69,69,69,69,769,69,69],\
        "humid" : [0,40,40,40,40,40,40,40],\
#        ,\
        
        "batt" : [0,80,80,80,80,80,80,80],\
        "rtime" : [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0],\
        "num_sends" : 0} # inc after send so start with 1

th_json={   # tempture/humidity sensor json dict
    "type_dev" : "",
    "unit" : "",
    "rnum" : 0,
    "temp": 70.0,
    "humid": 40,
    "batt": 99,    # battery % charge
    "rssi" : -62,   # receiver RF signal level
    "rtime" : 0,  # 
    "rtod" : ""
}

io_update={
    'device' : '',
    'data' : [0,0,0,0,0,0,0,0,0,0]  # 0-9 each is True/False(1/0) or int
}


