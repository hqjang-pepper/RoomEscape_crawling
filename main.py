import xphobia
import keyEscape
import codeK
import solvergd
import hoteldeCode
import masterKey
import nextEdition
import seoulEscapeRoom
import time
import datetime
import os
import pymysql
from multiprocessing import Process

day_written_file = open('C:/Users/Administrator/Desktop/crawling/day.txt')
days = int(day_written_file.read())
logfile = open('C:/Users/Administrator/Desktop/crawling/log.txt','a')

now = time.localtime()
a = time.time()
trial_time = "%04d-%02d-%02d %02d:%02d" % (now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min)
logfile.write(str(datetime.datetime.now())+"\n")

#실행하는 부분



try:
    keyEscape.crawling(days,trial_time)
    logfile.write(str(datetime.datetime.now())+"\t")
    logfile.write('keyescape complete\n')
except:
    logfile.write('keyescape error\n')

try:
    seoulEscapeRoom.crawling(days,trial_time)
    logfile.write(str(datetime.datetime.now())+"\t")
    logfile.write('seoulescaperoom complete\n')
except:
    logfile.write('seoulescaperoom error\n')

try:
    masterKey.crawling(days,trial_time)
    logfile.write(str(datetime.datetime.now())+"\t")
    logfile.write('masterkey complete\n')
except:
    logfile.write('masterkey error\n')

try:
    nextEdition.crawling(days,trial_time)
    logfile.write(str(datetime.datetime.now()) + "\t")
    logfile.write('nextedition complete\n')
except:
    logfile.write('nextedition error\n')

try:
    solvergd.crawling(days,trial_time)
    logfile.write(str(datetime.datetime.now()) + "\t")
    logfile.write('solvergd complete\n')
except:
    logfile.write('solvergd error\n')

try:
    hoteldeCode.crawling(days,trial_time)
    logfile.write(str(datetime.datetime.now()) + "\t")
    logfile.write('hoteldecode complete\n')
except:
    logfile.write('hoteldecode error\n')

try:
    codeK.crawling(days,trial_time)
    logfile.write(str(datetime.datetime.now()) + "\t")
    logfile.write('codeK complete\n')
except:
    logfile.write('codeK error\n')


# p1.start()



b=time.time()
now2 = time.localtime()
logfile.write("running time: ")
logfile.write(str(b-a))
logfile.write("\n\n")
logfile.close()
