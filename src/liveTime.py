###Get live timestamp###

import utime,ntptime,time
from src.mqtt import Connection
def timestamp():
    ntptime.settime() # to take the real time from the internet
    t = utime.localtime()
    year = str(t[0])
    month = str(t[1])
    day = str(t[2])
    hour = str(t[3] + 3)
    minute = str(t[4])
    second = str(t[5])
    
    if len(month) == 1:
        month = "0" + month
    if len(day) == 1:
        day = "0" + day
    if len(hour) == 1:
        hour = "0" + hour
    if len(minute) == 1:
        minute = "0" + minute
    if len(second) == 1:
        second = "0" + second
        
    time = day + "-" + month + "-" + year + " " + hour + ":" + minute + ":" + second
    
    return time


