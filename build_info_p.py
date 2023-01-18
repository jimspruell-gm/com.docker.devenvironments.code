# build_info_p.py   1-5-23 2014

import os
import sys
import time as tim
import json
import lems_time as lt
import requests

from baconfig3 import * #  class gc.  & json dicts

def con_log(strng):  # now only startup, th_json, and errors logged 
    tim.sleep(0.1)
    print(strng)
'''   
    fname = "th_post.log"
    log_file = open(fname,"a")     # open or create and append to end 
    log_file.write(strng + "-" + lt.rtod(tim.time()) + "\n\n") # line per record with blank line seperator
    log_file.close()
    return()   

'''
# -------------------------- post_log  2 strings  ------------------

def post_log(s1,s2):
    log_dict = {"name" : s1,"jstrng" : s2}
    try:
        x = requests.post(gc.log_url, json = log_dict)
    except:
        strng = ("21 request post(%s {%s}) failed" % (gc.log_url,json.dumps(log_dict)))
        con_log(strng)

# ---------- post json - goes to gc.log_url  same as post_log-----------------

def post_json(dict): #
    gc.post_time = tim.time()
    try:
        x = requests.post(gc.log_url, json = dict)
    except:
        strng = ("30 request post(%s {%s}) failed" % (gc.log_url,json.dumps(dict)))
        con_log(strng)


# ------------------ th_filter(rnum,this,sent) ----------------
# store 5 values, toss max & min, avg remaining 3 compare & send
#  chgd json only if avg changed by GT 1.7*F
# returns chgd,temp     

def th_filter(rnum,this_tmp,last_tmp):
    fmax = 0.0 #  max for this units
    fmin = 200.0 #  max for this units
    maxat = 0  # max at this 0-4 location for the current unit averaged
    minat = 0  # min at this 0-4 location for the current unit averaged

    fl.tmp[rnum][fl.ucnt[rnum]] = this_tmp  # store 0-4
    
    if (fl.ucnt[rnum] < 4): # just store 0-4
#        if (rnum == 1):
#            print("save rnum=1 cnt=%d tmp=%4.1f*F " % (fl.ucnt[rnum],this_tmp) )
        fl.ucnt[rnum] += 1
        return(0,int(this_tmp)) # not changed no send, just return

#------------- have 5  find max & min ----------
# fl.ucnt[rnum] == 4  ---  analize 5 values for the 5th temp just received
#    if (rnum == 1):
#        print("save rnum=1 cnt=%d tmp=%4.1f*F " % (fl.ucnt[rnum],this_tmp) )

    fl.ucnt[rnum] = 0  # set for next read
    fmax = 0.0 
    fmin = 200.0
    for ii in range(0,5):  # find where max and min at 
        if (fl.tmp[rnum][ii] > fmax): 
          fmax = fl.tmp[rnum][ii]
          maxat = ii

        if (fl.tmp[rnum][ii] < fmin): 
          fmin = fl.tmp[rnum][ii]
          minat = ii

#    if (rnum == 1):
#        print("rnum=1 maxat=%d minat=%d" % (maxat,minat) )
# have max & min toss those and average other 3 -------------------
    tottmp = 0.0
    avgcnt = 0
    chgd = 0
    for ii in range(0,5):  # look at 5 count all that are not max or min
        if ( (ii != minat) and (ii != maxat) ):
            tottmp += fl.tmp[rnum][ii]
            avgcnt += 1
# have good avg-----------------------
    gc.th_info["rtime"][rnum] = tim.time()
    gc.count[rnum] += 1
    gc.totalcnt += 1
    avgtmp = tottmp/float(avgcnt)
    deltatmp = abs( avgtmp - float(last_tmp) )

    if (deltatmp > 1.7):
        chgd = 1
        strng=("%s temp=%4.1f*F chg=%4.1f last=%d*F %s\n" % \
            (gc.th_info["room"][rnum],avgtmp,deltatmp,last_tmp,lt.rtod(tim.time())) )
        con_log(strng)
        post_log("tmp_chg",strng)  # log only if one changed
        post_json(gc.th_info)  # send th_info when temp changes

    if ((tim.time() - gc.post_time) > 30.0): # post_th every 30 sec 
        chgd = 1
    return(chgd,int(avgtmp))


# ------------ print th_json -----------------------

def dsp(th_json):   
#    th_json = json.loads(jstring)     
    strng = ('%s %3d*F Humid:%3d%% batt:%3d%% rssi:%3d %s %d' \
        % (th_json['unit'],th_json['temp'],\
        th_json['humid'],th_json['batt'],th_json['rssi'], \
        lt.rtod(th_json['rtime']),gc.totalcnt  ) )
    con_log(strng)



# ------- recv_json actually build local th_info & send th_json only if temp change--
def recv_json(th_json):  # th_json{} received from app.py

    rnum = th_json["rnum"]
# -- filter 5 samples and test if this avgd sample's temp that changed  
    chgd,newtemp = th_filter(rnum,th_json["temp"],gc.th_info["temp"][rnum]) 
    if (chgd == 0):  # temp did not change or not timeout
        return() 

#  -------a temp chgd enough, send it 
    gc.last_update = int(tim.time())
    gc.th_info["temp"][rnum] = newtemp

    gc.th_info["humid"][rnum] = th_json["humid"]
    gc.rssi[rnum] = th_json["rssi"]
    gc.th_info["batt"][rnum] = th_json["batt"]

    gc.totalcnt += 1

    gc.th_info["rtime"][rnum] = tim.time()  # time temp-humid was read 
    gc.dsp_rec["rtod"][rnum] = lt.rtod(tim.time())
# this th_json now in proper [rnum] of gc.th_info
    gc.cnt += 1
    if (gc.dbug):  # display only if debug set
        dsp(th_json)

    post_json(th_json)  # post only when temp changes


# ------------------start here ----------------------------------------

# wait 2 seconds for ba_web-app to start and get ready to receive requests
tim.sleep(2)
 
num_argv = len(sys.argv)
if (num_argv > 1):
    argv1 = sys.argv[1]
    if (argv1 == "1"):
        gc.th_info["room"] = gc.room1
        gc.unit = gc.unit1

    elif (argv1 == "2"):
        gc.th_info["room"] = gc.room2
        gc.unit = gc.unit2


    else:
        con_log("error argv[1] should be 1 or 2 but=" + str(sys.argv[1]) )
        sys.exit(1)

for rnum in range(1,len(gc.unit) ):  # why not ??
    gc.th_info["rtime"][rnum] = tim.time() - 60.0   # sec-old read around 70 before