  
#   now app.py  th_post version   1-5-23 1944 # now floating point temp
#    
#  
#   
# note battery% is 20% =~ 2Volts, 67%  2.73Volts, 89% is 2.84Volts
#  made from from open source goveWatch.py  

import os
import sys
from bleson import get_provider, Observer, UUID16
from bleson.logger import log, set_level, ERROR, DEBUG
import json
import time as tim
import lems_time as lt
import th_post_app as tp
import build_info_p as bi
from baconfig3 import *

#from flask import Flask, request, jsonify

class gl:
    start_time = 0.0
    cytime = 0
    mxcytime = 0
    error_count = 0
    name = ""


th_json={   # tempture/humidity sensor json dict
    "name" : "th_json",
    "type_dev" : "",   #typical "GVH5075", 
    "unit" : "",         #typical "7E88"
    "rnum" : 0,
    "temp": 70.0,
    "humid": 40,
    "batt": 99,    # battery % charge
    "rssi" : -62,   # receiver RF signal level
    "rtime" : 0,  # time of day
    "rtod" : ""

}

log_dict={
    "name" : "wr_log",# name of this dict{}
    "logname" : "",   # name of log file  "ERROR" , "th_json" ...
    "logstring" : ""  # json.dumps(json{}) or a string )
}

'''
def con_log(strng):
    tim.sleep(0.1)
    fname = "th_post.log"
    log_file = open(fname,"a")     # open or create and append to end 
    log_file.write(strng + "-" + lt.rtod(tim.time()) + "\n\n") # line per record with blank line seperator
    log_file.close()
    return()  
'''

def snd_error(strng):
    tp.post_log("ERROR",strng)
    gl.error_count += 1
    getus()  # ble_processing_time

# Disable warnings
set_level(ERROR)

# # Uncomment for debug log level
# set_level(DEBUG)

# https://macaddresschanger.com/bluetooth-mac-lookup/A4%3AC1%3A38
# OUI Prefix	Company
# A4:C1:38	Telink Semiconductor (Taipei) Co. Ltd.

GOVEE_BT_mac_OUI_PREFIX = "A4:C1:38"

H5075_UPDATE_UUID16 = UUID16(0xEC88)

govee_devices = {}

# ###########################################################################
FORMAT_PRECISION = ".2f"

'''
def dsp(th_json):  #jstring):
#    th_json = json.loads(jstring)     
    strng = ('%s  %3d*F  Humid:%3d%%   (batt:%3d%% rssi:%3d %s)' \
        % (th_json['unit'],th_json['temp'],\
        th_json['humid'],th_json['batt'],th_json['rssi'], lt.rtod(th_json['rtime'])  ) )
    con_log(strng)

'''
def getus():
    gl.cyime = tim.time() - gl.start_time
    if (gl.cytime > gl.mxcytime): 
        gl.mxcytime = gl.cytime


def build_th_json(mac,name):  # called by on_advertisement(advertisement) when BLE info received
# BLE data from sensor
#    print('\n got mac(%s) name(%s) \n' % (str(mac),str(name)) )
#    con_log(strng)
    gl.start_time = tim.time()
    govee_device = govee_devices[mac]
    try:
        type_dev = name[0:7]   # 1-7 'GVH5075' govee_device['name']
        if (type_dev != 'GVH5075' ):
            strng = "(tap104) GOVEE mac=%s bad device_type(%s) %s "  % \
                 ( mac, name,lt.rod(tim.time()))
            snd_error(strng)
            return() #bad device_type
       
    except:  # bad name 
        strng = "(tap110)%s ble_recv_data.py line 307 mac=%s except get name(%s)"  %\
         (lt.tod(tim.time()), mac, name)
        snd_error(strng)
        return()

# have good GVH5075 device 
    unit = name[8:12]      # 9-12 typical = 'AFF6'

    try:
        tempf = float(govee_device['tempInF'])
#        temp = tempf
        hum = float(govee_device['humidity'])
        humid = int(hum)                            # accurate to only 3% pass as int 
        batt = int(govee_device['battery'])
        rssi = int(govee_device['rssi'])

    except:  # ************ error record broadcast and then reboot this device
        strng = "\n(tap128) ***GOVEE ERROR %s mac=%s name(%s) exception " % \
            (lt.rtod(tim.time()),mac,name) 
        snd_error(strng)
        return()  # can't read th

    found = 0
    for rnum in range(len(gc.unit) ):  
        if (gc.unit[rnum] == unit):
            th_json["rnum"] = rnum  # room number
            found = 1
            break

    if (found != 1):
        strng = "\n(tap141) ***GOVEE unit %s not in list " % (unit, gc.unit)
        snd_error(strng)
        return()  

    th_json['type_dev'] = type_dev
    th_json['unit'] = unit
    th_json['temp'] = tempf  # now floating point temp
    th_json['humid'] = humid
    th_json['batt'] =  batt
    th_json['rssi'] =  rssi 
    th_json['rtime'] = tim.time()
    th_json["rtod"] = lt.rtod(tim.time())

    getus()  # ble_processing_time
#   tp.post_json(th_json)  # send th_json to ba_web/app.py
    bi.recv_json(th_json)
    return()

# Decode H5075 Temperature into degrees Celcius
def decode_temp_in_c(encoded_data):
    return format((encoded_data / 10000), FORMAT_PRECISION)


# Decode H5075 Temperature into degrees Fahrenheit
def decode_temp_in_f(encoded_data):
    return format((((encoded_data / 10000) * 1.8) + 32), FORMAT_PRECISION)


# Decode H5075 percent humidity
def decode_humidity(encoded_data):
    return format(((encoded_data % 1000) / 10), FORMAT_PRECISION)


# On BLE advertisement callback
def on_advertisement(advertisement):
#    log.debug(advertisement)

    if advertisement.address.address.startswith(GOVEE_BT_mac_OUI_PREFIX):
        mac = advertisement.address.address

        if mac not in govee_devices:
            govee_devices[mac] = {}
        if H5075_UPDATE_UUID16 in advertisement.uuid16s:
            # HACK:  Proper decoding is done in bleson > 0.10
            gl.name = str(advertisement.name) #.split("'")[1]
            
#            print('\n adver.name(%s) \n' % gl.name)

            encoded_data = int(advertisement.mfg_data.hex()[6:12], 16)
            battery = int(advertisement.mfg_data.hex()[12:14], 16)
            govee_devices[mac]["address"] = mac
            govee_devices[mac]["name"] = gl.name
            govee_devices[mac]["mfg_data"] = advertisement.mfg_data
            govee_devices[mac]["data"] = encoded_data

            govee_devices[mac]["tempInC"] = decode_temp_in_c(encoded_data)
            govee_devices[mac]["tempInF"] = decode_temp_in_f(encoded_data)
            govee_devices[mac]["humidity"] = decode_humidity(encoded_data)

            govee_devices[mac]["battery"] = battery
#           print_values(mac)

        if advertisement.rssi is not None and advertisement.rssi != 0:
            govee_devices[mac]["rssi"] = advertisement.rssi
#            print('name=%s' % gl.name )
            gl.start_time = tim.time() # -------------------- start time -------
            build_th_json(mac,gl.name) #  bld_auto system call to sverage and store record !!!!!!!!!!!!!!
#        log.debug(govee_devices[mac])


# ##########################  starts here #################################################

def govee_start():

    adapter = get_provider().get_adapter()

    observer = Observer(adapter)
    observer.on_advertising_data = on_advertisement

    try:
        while True:
            observer.start()
            tim.sleep(2)
            observer.stop()
         
    except KeyboardInterrupt:
        try:
            observer.stop()
            sys.exit(0)
        except SystemExit:
            observer.stop()
            os._exit(0)

#  start here            
tim.sleep(2)  # allow goveestate to startup first
govee_start()


