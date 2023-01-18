# lems_time.py with float rtod()
# 10-16-22 2100  updated rtod() as string added ret_dtime(strng,start) time_since(), get_tod(time()) & int_ydh(time())

import os
import sys
from time import localtime, strftime, sleep, time, mktime
# coding: utf-8 -*-
from datetime import datetime, tzinfo

istarttime = [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0] # 0-9 allowed inx values

def time_since(start_time):  # return float of time since start time
    return(time() - start_time)

def str_time(intime):
    tstr = strftime("%a_%b_%d_%Y_%H:%M:%S",localtime(intime))
    return(tstr)

def minsec(intime):  # time of day 
    tstr = strftime("%M:%S",localtime(intime))
    return(tstr)

def tod(intime):  # time of day 
    tstr = strftime("%H:%M:%S",localtime(intime))
    return(tstr)

def int_hour(intime):
    hstr = strftime("%H",localtime(intime))
    return(int(hstr))

def ret_hms(intime):
    hour = int( strftime("%H",localtime(intime)) )
    minn = int( strftime("%M",localtime(intime)) )
    sec = int( strftime("%S",localtime(intime)) )
    return(hour,minn,sec)


def ret_mdh(intime):  # return string-month,int-day,int-hour
    month = strftime("%b",localtime(intime))  # return string ie 'Apr'
    hour = int( strftime("%H",localtime(intime)) )
    day = int( strftime("%d",localtime(intime)) )
    return(month,day,hour)


def dt2str(time_in): # return string date & time
    tstr = strftime("%w  %x %H:%M:%S",localtime(time_in))
    if (tstr[0:1] == '0' ): # day of week 0=sunday 6=saturday
        wday = 'Su '
    elif (tstr[0:1] == '1' ):
        wday = 'Mo '
    elif (tstr[0:1] == '2' ):
        wday = 'Tu '
    elif (tstr[0:1] == '3' ):
        wday = 'We '
    elif (tstr[0:1] == '4' ):
        wday = 'Th '
    elif (tstr[0:1] == '5' ):
        wday = 'Fr '
    elif (tstr[0:1] == '6' ):
        wday = 'Sa '
    return(wday + tstr[3:25])

# 5 ints to datetime, enter only (year-2000), month, day, hour, minute
def ints2time(iyr,imo,iday,ihour,iminute): # int(dtime) set to  minutes seconds=0.0
    time_tuple = ((iyr + 2000),imo,iday,ihour,iminute,0,0,0,-1)
    #note -1 is same format and timezone as localtime()
    timestamp = mktime(time_tuple)
    return(timestamp)

def ret_dtime(strng,start):  # delta time
    return(strng,(time() - start))    

def rtod(intime):# string readable time of day
    ms = int( (intime % 1) * 1000)
    hour,minn,sec = ret_hms(intime)
    strng =  str(hour).zfill(2) + ":" + str(minn).zfill(2) + ":" + str(sec).zfill(2)  + "." +str(ms).zfill(3)
    return(strng)

def stod(intime):# string time of day
    ms = int( (intime % 1) * 1000)
    hour,minn,sec = ret_hms(intime)
    strng = str(hour).zfill(2) + 'Hr ' + str(minn).zfill(2) + 'Min ' + str(sec).zfill(2) + '.'  + str(ms).zfill(3) + 'Sec'
    return(strng)


def fname(logname,day_delta): # dictname_m0-day-yr 
    day_time_offset = float(day_delta * 86400.0) #seconds in day=(60*60*24)=86400
    day_time =  time()  + day_time_offset
    strng = "%s_%s" % (logname,str_mdy(day_time,"-")) #name_10-16-2022
    return(strng)



def sec2hms(s10k): # seconds to ihr,iminn,fsec
    dsec = (s10k % 10000)/10000.0  # fractional sec
    isec = int(s10k)/10000
    tminn = isec/60
    sec = float(tminn % 60) + dsec
    hr = tminn/60 
    minn = tminn % 60
    return(hr,minn,sec)

def rtod2sec(srtod): # rtod string to seconds
    todlst = list(srtod.split(":"))
    hr = int(todlst[0])
    minn = int(todlst[1])
    sec = float(todlst[2])
    todsec = float(hr * 3600 + minn*60) + sec
#    todtxt = ("hr=%d minn=%d sec=%5.4f todsec=%5.3f" % (hr,minn,sec,todsec))
#    print(todtxt)
    return(todsec)  # return number of seconds.000 since midnight

def sec2rtod(secsmn):  # seconds since midnight to rtod
    ms = secsmn % 1.0  # ms remainder
    tsec = int(secsmn)  # total int sec
    hr = tsec/3600
    hrrem = tsec % 3600  # sec remain after hr
    minn = hrrem / 60
    isec = hrrem % 60  # sec remain after minn
    sec = float(isec) + ms

    strng = "%d:%d:%4.3f" % (hr,minn,sec)
    return(strng)


def ret_mdy(intime):
    yr = int( strftime("%Y",localtime(intime)) )
    mo = int( strftime("%m",localtime(intime)) )
    day = int( strftime("%d",localtime(intime)) )
    return(mo,day,yr)

def str_mdy(intime,sep_char):
    mo,day,yr = ret_mdy(intime)
    strng= "%d%s%d%s%d" % (mo,sep_char,day,sep_char,yr)
    return(strng)

def dmytimestr(intime):
   strng = "%s_%s" % ( str_mdy(intime,"-"), rtod(intime) )
   return(strng)

'''
# 
print("%s" % dmytimestr(time()) )#  10-16-2022_21:20:24.111 23char

mo,day,yr = ret_mdy(time())
print ("ret_mdy=%d,%d,%d" % (mo,day,yr))
print("str:=%s" % str_mdy(time(),":"))
print("str/=%s" % str_mdy(time(),"/"))
print("fname=%s" % fname("logname",-1))

tim = time()
str1 = rtod(tim)
fsec = rtod2sec(str1) # to float sec since midnight
str2 = sec2rtod(fsec)

print("%s = %4.3f = %s" % (str1,fsec,str2) )

tim = time()
str1 = rtod(tim)
fsec = rtod2sec(str1) # to float sec since midnight
str2 = sec2rtod(fsec)

#print(rtod(tim))
#print(rtod2sec(rtod(tim)) )
#print(rtod2sec(rtod(tim +10.1) ) )

print("0=%s 2=%s -1=%s" % (fname("jdict0",0),fname("jdict2",2),fname("jdict-1",-1)))

s10k = sec10k(time())
hr,minn,sec = s10k2t(s10k)
print("s10k=%d:%d:%5.4f" % (hr,minn,sec) )
print("name=%s s10k=%d %s" % (tblname("jsonname"),s10k,s10ktxt(s10k)) )


print(rtod(time()) )
s10k = sec10k(time())
print("sec10k=%d " % s10k)
hr,minn,sec = s10k2t(s10k)
print("s10k=(%d) %d:%d:%f" % (s10k,hr,minn,sec) )


print("%d/%d/%d-%d:%d:%8.6f" % (mo,day,yr,hr,mn,sec) )

#ms10= itime10ms(time())

#ntime = i10ms2time(ms10)

#print("m10ms=(%d) time=(%10.4f)" % (ms10,ntime) )

#print("(%s)" % rtod(time()) )   

#print(stod(time()) )

    
#num = rtod(time())
#`print( rtod(time()) )
    

def rtod_ms(rtodval):
    stng = str(rtodval)
    lenn = len(stng)
    if (lenn == 8):
        hr=int(stng[0:1])
        minn=int(stng[1:3])
        sec = int(stng[3:5])
        ms = int(stng[5:8])
    elif (lenn==9):
        hr=int(stng[0:2])
        minn=int(stng[2:4])
        sec = int(stng[4:6])
        ms = int(stng[6:9])
    elif (lenn==7): # must be no 0 for hour & 2 digit minn
        hr = 0
        minn=int(stng[0:2])
        sec = int(stng[2:4])
        ms = int(stng[4:7])
    elif (lenn==6): # must be no 0 for hour & 1 digit minn
        hr = 0
        minn=int(stng[0:1])
        sec = int(stng[1:3])
        ms = int(stng[3:6])
    else:
        print("error returned input value:%d " % rtodval )
        return(rtodval)

    ret = (hr * 3600000) + (minn * 60000) + (sec * 1000) + ms
    print('ret=%d' % ret)


def delta_rtod(t1,t2): # delta ms (t2 - t1)
    ret = rtod_ms(t2) - rtod_ms(t1)
    return(ret)

t1= 90201023
t2 = 90202023  

ret = delta_rtod(t1,t2) 
print(ret)


num = rtod(time())
print(num)

start = time()
sleep(1)
print('%s %4.6f' % (ret_dtime('1 sec',start)) )

print('%s %4.6f' % (ret_dtime('#2',start)) ) 
print('%s %4.6f' % (ret_dtime('#3',start)) )
sleep(1.5)
print('%s %4.6f' % (ret_dtime('after 1,5 more',start)) )

    
print('tod=%s' % tod(time()))

print(strftime("%H:%M:%S",localtime(time())))

hr,mn,sec= ret_hms(time())
print('hour=%s min=%d sec=%d' % (hr,mn, sec) )
   
# test day_name(day_delta)
print('name of today (%s)' % day_name(0))
print('name of 1 day in future = (%s)' % day_name(1))
print('name of 1 day in past = (%s)' % day_name(-1))

# test of ret_mdh() & tod()
#month,day,hour = ret_mdh(time())
#print('month=%s day=%d hour=%d' % (month, day, hour) )
#print('(hr min sec='+tod(time())+')')

'''