#!/usr/bin/env python
from matplotlib import use
use('agg')
import pyart
import numpy as np
from matplotlib import pyplot as plt
import sys
import os
from netCDF4 import num2date
from time import sleep, time
import os
import sys
import shutil

def make_movie(pattern):
  indir='/data/ldm/images/'
  #pattern='KLOT'
  files=os.listdir(indir)
  good_files=[]
  for fl in files:
    if pattern in fl:
        good_files.append(fl)
  good_files.sort()
  last_30 = good_files[-100:]
  i=0
  for fl in last_30:
    nn="/data/tmp/atbmedia_%03d.png" %i
    print indir+fl, nn
    shutil.copyfile(indir+fl, nn)
    i+=1
  os.system('avconv -y -i /data/tmp/atbmedia_%03d.png -vcodec h264  /data/ldm/{0}_mov.mp4'.format(pattern))
  os.system('scp  /data/ldm/{0}_mov.mp4 scollis@atmos.anl.gov:/usr/share/tomcat/webapps/ROOT/quicklooks'.format(pattern))



if __name__=="__main__":
  sys.stderr = open('/data/ldm/errorlog.txt', 'w')
  sys.stdout = open('/data/ldm/print_log.txt', 'w')
  #quick sleep to ensure the last file is written
  sleep(5)
  date_str = sys.argv[1]
  odir = sys.argv[2]
  print "doing ", date_str, ' ', sys.argv[3]
  all_files = os.listdir(odir)
  targets = []
  for fname in all_files:
    if date_str in fname:
      targets.append(odir +'/'+ fname)
  com1 = 'cat ' + odir +'/' + date_str + '* > ' \
     + odir + '/' + sys.argv[3] + '_' + date_str+'.nexrad'
  targets.sort()
  #Concatinate all messages into a file
  os.system(com1)
  #remove messages
  for targ in targets:
    os.remove(targ)
  #now for the radar funbags!
  os.system('echo  read >>  /data/ldm/plot_log.txt')
  os.system('echo  read'+odir + '/' + sys.argv[3] + '_' \
                         + date_str+'.nexrad'+' >>  /data/ldm/plot_log.txt')
  radar = pyart.io.read(odir + '/' + sys.argv[3] + '_' + date_str+'.nexrad')
  os.system('echo HERE >>  /data/ldm/plot_log.txt')
  if sys.argv[3] == 'KLOT':
    lat = 41.7092
    lon = -87.9820
    max_lat = 43.
    min_lat =40
    min_lon = -90.5
    max_lon = -86
    display = pyart.graph.RadarMapDisplay(radar)
    f = plt.figure(figsize = [18,10])
    display.plot_ppi_map('reflectivity',   max_lat = max_lat, min_lat =min_lat,
                         min_lon = min_lon, max_lon = max_lon, vmin = -8,
                         vmax = 64,  lat_lines = np.arange(min_lat,max_lat,.5),
                         lon_lines = np.arange(min_lon, max_lon, 1),
                         resolution = 'l')
  elif sys.argv[3] == 'KVNX':
    lat = 41.7092
    lon = -87.9820
    max_lat = 38
    min_lat =36
    min_lon = -99
    max_lon = -96.5
    display = pyart.graph.RadarMapDisplay(radar)
    f = plt.figure(figsize = [18,10])
    display.plot_ppi_map('reflectivity',   max_lat = max_lat, min_lat =min_lat,
                        min_lon = min_lon, max_lon = max_lon, vmin = -8,
                        vmax = 64,  lat_lines = np.arange(min_lat,max_lat,.5),
                        lon_lines = np.arange(min_lon, max_lon, 1),
                         resolution = 'l')
  else:
    display = pyart.graph.RadarMapDisplay(radar)
    f = plt.figure(figsize = [18,10])
    display.plot_ppi_map('reflectivity',
                         vmin = -8, vmax = 64,
                         resolution = 'l')
  mydate = num2date(0, radar.time['units'])
  full_date_str = '{:%Y%m%d%H%M%S}'.format(mydate)
  #full_date_str = str(mydate.year) + str(mydate.month) \
  #                    + str(mydate.day) + str(mydate.hour) + str(mydate.minute)
  print full_date_str
  plt.savefig('/data/ldm/images/' + sys.argv[3]+ '_' + full_date_str + '.png')
  plt.savefig('/data/ldm/images/'+ sys.argv[3]+ '_latest.png')
  plt.close(f)
  os.system('scp '+'/data/ldm/images/' + sys.argv[3]+ '_latest.png ' + \
            'scollis@atmos.anl.gov:/usr/share/tomcat/webapps/ROOT/quicklooks/')
  make_movie(sys.argv[3])
  sys.stderr.close()
  sys.stdout.close()
