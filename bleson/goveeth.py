# goveeth.py   7-4-22 1017
#  read govee GVH5075 temp/humid sensor ble messages & send as a broadcast json socket    

# note battery%  20% =~ 2Volts, 67% =~ 2.73Volts, 89% =~ 2.84Volts
# when battery = 20% ~ 11 hours left before quits working 
# goveeth.py    made from from open source goveWatch.py
  
import json
from bauto_config import *

#from time import sleep,time
import time as tim
import os
import sys
from bleson import get_provider, Observer, UUID16
from bleson.logger import log, set_level, ERROR, DEBUG
import toss_mxmn_avg as ta 

import lems_time as lt
import socket


server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

# Enable port reusage so we will be able to run multiple clients and servers on single (host, port). 
# Do not use socket.SO_REUSEADDR except you using linux(kernel<3.9): goto https://stackoverflow.com/questions/14388706/how-do-so-reuseaddr-and-so-reuseport-differ for more information.
# For linux hosts all sockets that want to share the same address and port combination must belong to processes that share the same effective user ID!
# So, on linux(kernel>=3.9) you have to run multiple servers and clients under one user to share the same (host, port).
# Thanks to @stevenreddie
#server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)  # some python3 versionl need this line
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # and some need this line 
# Enable broadcasting mode
server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

# Set a timeout so the socket does not block
# indefinitely when trying to receive data.
server.settimeout(5)
#message = b"your very important message"
#while True:
def bcast(message):
    server.sendto(bytes(message, "utf-8"), ('255.255.255.255', 37020))
#    print(prtstring)


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

class gc:
    nspl = 5
    topic = "/bld_auto/temp_humid"
    client = '/bld_auto/GVH5075_mqtt'
    retopic = '/bld_auto/GOVEE_ERROR'
    ngtopic = '/bld_auto/new_GOVEE'      
    jstr = ''
    name = ''
    cnt = 0
    error_count = 0

# 5 readings, toss hi & low then average remaining 3 readings
dev =[
    {
        'dev' : 'GVH5075',
        'unit': 'CC87',  
        'loc' : 0,
        'cnt' : 0,
        'seq' : 1,
        'tmp' : [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0],
        'hum' : [0,0,0,0,0,0,0,0,0,0,0,0,0],
        'batt' : [0,0,0,0,0,0,0,0,0,0,0,0,0],
        'rssi' : [0,0,0,0,0,0,0,0,0,0,0,0,0]
    },
    {
        'dev' : 'GVH5075',
        'unit' : '9999',  
        'loc' : 0,
        'cnt' : 0,
        'seq' : 1,
        'tmp' : [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0],
        'hum' : [0,0,0,0,0,0,0,0,0,0,0,0,0],
        'batt' : [0,0,0,0,0,0,0,0,0,0,0,0,0],
        'rssi' : [0,0,0,0,0,0,0,0,0,0,0,0,0]
    },

    {
        'dev' : 'GVH5075',
        'unit' : '1CB0',
        'loc' : 0,
        'cnt' : 0,
        'seq' : 1,
        'tmp' : [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0],
        'hum' : [0,0,0,0,0,0,0,0,0,0,0,0,0],
        'batt' : [0,0,0,0,0,0,0,0,0,0,0,0,0],
        'rssi' : [0,0,0,0,0,0,0,0,0,0,0,0,0]
    },
    {
        'dev' : 'GVH5075',
        'unit' : '4298',
        'loc' : 0,
        'cnt' : 0,
        'seq' : 1,
        'tmp' : [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0],
        'hum' : [0,0,0,0,0,0,0,0,0,0,0,0,0],
        'batt' : [0,0,0,0,0,0,0,0,0,0,0,0,0],
        'rssi' : [0,0,0,0,0,0,0,0,0,0,0,0,0]
    },
    {
        'dev' : 'GVH5075',
        'unit' : '8FBF',
        'loc' : 0,
        'cnt' : 0,
        'seq' : 1,
        'tmp' : [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0],
        'hum' : [0,0,0,0,0,0,0,0,0,0,0,0,0],
        'batt' : [0,0,0,0,0,0,0,0,0,0,0,0,0],
        'rssi' : [0,0,0,0,0,0,0,0,0,0,0,0,0]
    },
    {
        'dev' : 'GVH5075',
        'unit' : '23EC',
        'loc' : 0,
        'cnt' : 0,
        'seq' : 1,
        'tmp' : [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0],
        'hum' : [0,0,0,0,0,0,0,0,0,0,0,0,0],
        'batt' : [0,0,0,0,0,0,0,0,0,0,0,0,0],
        'rssi' : [0,0,0,0,0,0,0,0,0,0,0,0,0]
    },
    {
        'dev' : 'GVH5075',
        'unit' : '7E88',
        'loc' : 0,
        'cnt' : 0,
        'seq' : 1,
        'tmp' : [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0],
        'hum' : [0,0,0,0,0,0,0,0,0,0,0,0,0],
        'batt' : [0,0,0,0,0,0,0,0,0,0,0,0,0],
        'rssi' : [0,0,0,0,0,0,0,0,0,0,0,0,0]
    },
    {
        'dev' : 'GVH5075',
        'unit' : 'D821',
        'loc' : 0,
        'cnt' : 0,
        'seq' : 1,
        'tmp' : [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0],
        'hum' : [0,0,0,0,0,0,0,0,0,0,0,0,0],
        'batt' : [0,0,0,0,0,0,0,0,0,0,0,0,0],
        'rssi' : [0,0,0,0,0,0,0,0,0,0,0,0,0]
    },
    {
        'dev' : 'GVH5075',
        'unit' : '19A0',
        'loc' : 0,
        'cnt' : 0,
        'seq' : 1,
        'tmp' : [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0],
        'hum' : [0,0,0,0,0,0,0,0,0,0,0,0,0],
        'batt' : [0,0,0,0,0,0,0,0,0,0,0,0,0],
        'rssi' : [0,0,0,0,0,0,0,0,0,0,0,0,0]
    },
    {
        'dev' : 'GVH5075',
        'unit' : '99A1',
        'loc' : 0,
        'cnt' : 0,
        'seq' : 1,
        'tmp' : [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0],
        'hum' : [0,0,0,0,0,0,0,0,0,0,0,0,0],
        'batt' : [0,0,0,0,0,0,0,0,0,0,0,0,0],
        'rssi' : [0,0,0,0,0,0,0,0,0,0,0,0,0]
    },
    {
        'dev' : 'GVH5075',
        'unit' : 'C30B',
        'loc' : 0,
        'cnt' : 0,
        'seq' : 1,
        'tmp' : [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0],
        'hum' : [0,0,0,0,0,0,0,0,0,0,0,0,0],
        'batt' : [0,0,0,0,0,0,0,0,0,0,0,0,0],
        'rssi' : [0,0,0,0,0,0,0,0,0,0,0,0,0]
    },
    {
        'dev' : 'GVH5075',
        'unit' : 'A430',
        'loc' : 0,
        'cnt' : 0,
        'seq' : 1,
        'tmp' : [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0],
        'hum' : [0,0,0,0,0,0,0,0,0,0,0,0,0],
        'batt' : [0,0,0,0,0,0,0,0,0,0,0,0,0],
        'rssi' : [0,0,0,0,0,0,0,0,0,0,0,0,0]
    },
    {
        'name' : 'GVH5075',
        'unit' : '097D',
        'loc' : 0,
        'cnt' : 0,
        'seq' : 1,
        'tmp' : [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0],
        'hum' : [0,0,0,0,0,0,0,0,0,0,0,0,0],
        'batt' : [0,0,0,0,0,0,0,0,0,0,0,0,0],
        'rssi' : [0,0,0,0,0,0,0,0,0,0,0,0,0]
    },
    {
        'dev' : 'GVH5075',
        'unit' : 'AFF6',
        'loc' : 0,
        'cnt' : 0,
        'seq' : 1,
        'tmp' : [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0],
        'hum' : [0,0,0,0,0,0,0,0,0,0,0,0,0],
        'batt' : [0,0,0,0,0,0,0,0,0,0,0,0,0],
        'rssi' : [0,0,0,0,0,0,0,0,0,0,0,0,0]
    },
# for up to 4 unregistered units    
    {
        'dev' : 'GVH5075',
        'unit' : '0000',
        'loc' : 0,
        'cnt' : 0,
        'seq' : 1,
        'tmp' : [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0],
        'hum' : [0,0,0,0,0,0,0,0,0,0,0,0,0],
        'batt' : [0,0,0,0,0,0,0,0,0,0,0,0,0],
        'rssi' : [0,0,0,0,0,0,0,0,0,0,0,0,0]
    },
        {
        'dev' : 'GVH5075',
        'unit' : '0000',
        'loc' : 0,
        'cnt' : 0,
        'seq' : 1,
        'tmp' : [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0],
        'hum' : [0,0,0,0,0,0,0,0,0,0,0,0,0],
        'batt' : [0,0,0,0,0,0,0,0,0,0,0,0,0],
        'rssi' : [0,0,0,0,0,0,0,0,0,0,0,0,0]
    },
    {
        'dev' : 'GVH5075',
        'unit' : '0000',
        'loc' : 0,
        'cnt' : 0,
        'seq' : 1,
        'tmp' : [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0],
        'hum' : [0,0,0,0,0,0,0,0,0,0,0,0,0],
        'batt' : [0,0,0,0,0,0,0,0,0,0,0,0,0],
        'rssi' : [0,0,0,0,0,0,0,0,0,0,0,0,0]
    },
        {
        'dev' : 'GVH5075',
        'unit' : '0000',
        'loc' : 0,
        'cnt' : 0,
        'seq' : 1,
        'tmp' : [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0],
        'hum' : [0,0,0,0,0,0,0,0,0,0,0,0,0],
        'batt' : [0,0,0,0,0,0,0,0,0,0,0,0,0],
        'rssi' : [0,0,0,0,0,0,0,0,0,0,0,0,0]
    }            
]

'''
bcast_msg={
    "rec_type" : '',  # 'error'  or 'th_json' record 
    'jstring' : '' # string of error or data json record
}
'''

def snd_json(type,jstring):  # type is string 'error' or 'rec_type'
    bcast_msg['rec_type'] = type
    bcast_msg['jstring'] = jstring
    pstring = json.dumps(bcast_msg)
#    print('bcast(%s) \n' % pstring )
    bcast(pstring)
    if (type == 'th_json' ): 
        print('%s-%s %4.1f*F Humid:%3d%% batt:%3d%% rssi:%3d %s ' \
          % (th_json['type_dev'],th_json['unit'],th_json['temp'],\
          th_json['humid'],th_json['batt'],th_json['rssi'], lt.tod(th_json['rtime'])  ) )
    else:
        print('%s %s' % (type,jstring))

def error():  # reboot if gc.error_count > 3 else return
    gc.error_count += 1
    if (gc.error_count < 4):
        return()
    print(strng,'\n rebooting in 10 seconds')
    tim.sleep(10)    # time for broadcast to be sent
    os.system('sudo reboot')

def build_record(mac,name):  # called by on_advertisement(advertisement) when BLE info received
# BLE data from sensor
#    print('\n got mac(%s) name(%s) \n' % (str(mac),str(name)) )    
    govee_device = govee_devices[mac]
    try:
        type_dev = name[0:7]   # 1-7 'GVH5075' govee_device['name']
        if (type_dev != 'GVH5075' ):
            strng = "%s govee_stand_alone3.py 305 mac=%s bad device_type(%s)"  % (lt.tod(tim.time()), mac, name)
            error()
            return() #bad device_type
       
    except:  # bad name 
        strng = "%s govee_stand_alone3.py 310 mac=%s except get name(%s)"  % (lt.tod(tim.time()), mac, name)
        snd_json('GOVEE_ERROR',strng)  # error record from BLE 
        error()
        return()

    try:

        tempf = float(govee_device['tempInF'])
        hum = float(govee_device['humidity'])
        humid = int(hum)                            # accurate to only 3% pass as int 
        batt = int(govee_device['battery'])
        rssi = int(govee_device['rssi'])
#        print('\ntemp(%s) humid(%d) batt(%d) \n' % (str(tempf),humid,batt) )
    except:  # ************ error record broadcast and then reboot this device

        strng = "\n ***GOVEE ERROR ***** %s goveSA 213 mac=%s name(%s) exception getting TH data " % \
            (lt.tod(tim.time()),mac,name) 

        snd_json('GOVEE ERROR',strng)  # error record from BLE delay and reboot
        error()
        return()  # can't read th

    unit = name[8:12]      # 9-12 typical = 'AFF6'
    in_dd = 0
    for dd in dev:
        if (dd['unit'] == unit):  # found or just added to dd[]
            in_dd = 1
        elif (dd['unit'] == '0000'):  # got to new blocks
            dd['unit'] = unit
            strng = 'new_Govee in dd[] type_dev(%s) unit(%s) T:%4.1fF H:%d%% batt:%d rssi:%d' \
            % (type_dev,unit, tempf,humid,batt,rssi)
# not an error just brodcast message
            snd_json('new_Govee added to dd[]',strng)  # new_Govee from BLE bcast strng
            in_dd = 1
        if (in_dd):
            break
            
# run thru all looking for this name
    if (in_dd == 0):  # not in table use govee_ident..py to identify the new unit
        strng = 'new Govee not in dd[] type(%s) unit(%s) T:%4.1fF H:%d%% batt:%d rssi:%d' % (type_dev,unit, tempf,humid,batt,rssi)
# not an error just brodcast message
        snd_json('new_Govee',strng)  # new_Govee from BLE bcast strng 
        return()

# name is in dev[]
# note: th_json{} is in bauto_config 
    for dd in dev:
        if (unit == dd['unit']):
            if (dd['cnt'] >  gc.nspl):  # already have full set of values
# average data already in dev[] 
                th_json['type_dev'] = type_dev
                th_json['unit'] = unit
                gc.cnt += 1
                dd['seq'] = gc.cnt
                th_json["seq"] = dd['seq']  # seq counts each read
# remove max & min then average other readings ****************************************               
                th_json['temp'] = ta.toss_mxmn_avg(dd['tmp'],gc.nspl,1)
                th_json['humid'] =  int(ta.toss_mxmn_avg(dd['hum'],gc.nspl,1))
                th_json['batt'] =  int(ta.toss_mxmn_avg(dd['batt'],gc.nspl,0))
                th_json['rssi'] =  int(ta.toss_mxmn_avg(dd['rssi'],gc.nspl,0))
                th_json['rtime'] = tim.time()

# setup average values sent 
                sq = th_json["seq"] 
                tmp = th_json['temp']
                hum = th_json['humid']
                bat = th_json['batt']
                rss = th_json['rssi']
# completed toss_avg, now store current sample in loc 0
                loc = 0  
                dd['cnt'] = 1  # this is 1 reading
                dd['tmp'][loc] = tempf
                dd['hum'][loc] = humid
                dd['batt'][loc] = batt
                dd['rssi'][loc] = rssi


#                strng = '%s %s sid:%d seq:%d T:%4.1f H:%d batt:%d rssi:%d' % \
#                        (dev_name, lt.tod(tim.time() ), sid,sq,tmp,hum,bat,rss)
#                print(strng)

                gc.jstr = json.dumps(th_json) # send when 5 samples have been received !!!!!!!!!
                snd_json('th_json',gc.jstr)  # max & min are tossed and other 3 averaged !!!!!!


# not this sid's sample 5  accumulate samples 0-4 for each sid   
            else:  # this isn't the last sample, just store itin proper dev[][loc] 
                loc = dd['cnt']
                dd['cnt'] += 1
                dd['tmp'][loc] = tempf
                dd['hum'][loc] = humid
                dd['batt'][loc] = batt
                dd['rssi'][loc] = rssi


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
    log.debug(advertisement)

    if advertisement.address.address.startswith(GOVEE_BT_mac_OUI_PREFIX):
        mac = advertisement.address.address

        if mac not in govee_devices:
            govee_devices[mac] = {}
        if H5075_UPDATE_UUID16 in advertisement.uuid16s:
            # HACK:  Proper decoding is done in bleson > 0.10
            gc.name = str(advertisement.name) #.split("'")[1]
            
#            print('\n adver.name(%s) \n' % gc.name)

            encoded_data = int(advertisement.mfg_data.hex()[6:12], 16)
            battery = int(advertisement.mfg_data.hex()[12:14], 16)
            govee_devices[mac]["address"] = mac
            govee_devices[mac]["name"] = gc.name
            govee_devices[mac]["mfg_data"] = advertisement.mfg_data
            govee_devices[mac]["data"] = encoded_data

            govee_devices[mac]["tempInC"] = decode_temp_in_c(encoded_data)
            govee_devices[mac]["tempInF"] = decode_temp_in_f(encoded_data)
            govee_devices[mac]["humidity"] = decode_humidity(encoded_data)

            govee_devices[mac]["battery"] = battery
#           print_values(mac)

        if advertisement.rssi is not None and advertisement.rssi != 0:
            govee_devices[mac]["rssi"] = advertisement.rssi
#            print('name=%s' % gc.name )
            build_record(mac,gc.name) #  bld_auto system call to sverage and store record !!!!!!!!!!!!!!
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


govee_start()
