import os
import argparse
from datetime import datetime, timezone
import glob
import sys
import yaml
import xml.etree.ElementTree as ET
import shutil

from obspy.core.utcdatetime import UTCDateTime


def main():
    '''
        Simple script to modify playback event ShakeAlert SA.xml with time = now
        and start tankplayer to begin releasing tankplayer packets onto the wave_ring
    '''

    seismic_tankplayer_file = "some/path/tankplayer.d"
    geodetic_tankplayer_file = "some/path/tankplayer.d"
    offset = 20.5251

    params_dir = os.environ.get('EW_PARAMS')
    cwd = os.getcwd()

    if params_dir is None:
        print("You must source an EW env before running this!")
        exit(2)

    #   So we adjust the OT by offset_time wrt actual first packet time:
    #timestamp = datetime.now(tz=timezone.utc).timestamp()
    #otime = datetime.utcfromtimestamp(timestamp).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    #print("         Now time:%s   [%f]" % (otime, timestamp))
    #timestamp = datetime.now(tz=timezone.utc).timestamp() + offset_time
    #timestamp = UTCDateTime.utcnow()
    #otime = UTCDateTime.utcnow() + offset_time
    #print("         Now time:%s" % timestamp)
    #print("Stamp origin time:%s" % otime)
    #print("    delay trigger:%.2f secs" % delay_trigger)
    #orig_time.text = orig_time.text.replace(orig_time.text, otime)

    thread_1 = myThread(1, "Thread-1", 0, seismic_tankplayer_file)
    thread_2 = myThread(2, "Thread-2", 0, geodetic_tankplayer_file)

    print("[%s] Start the seismic tankplayer" % datetime.now(tz=timezone.utc).timestamp())
    thread_1.start()
    time.sleep(offset)
    print("[%s] Start the geodetic tankplayer" % datetime.now(tz=timezone.utc).timestamp())
    thread_2.start()

    return

import threading
import time

exitFlag = 0

class myThread (threading.Thread):
   def __init__(self, threadID, name, counter, tankfile):
      threading.Thread.__init__(self)
      self.threadID = threadID
      self.name = name
      self.counter = counter
      self.tankfile = tankfile

   def run(self):
      print("*** Starting Python thread:" + self.name)
      os.system('tankplayer %s' % self.tankfile)

#def make_SA(lat, lon, time, depth, mag):
def make_SA(config, ot):

    evid = '1111'
    mag = 6.0
    lat_uncer = .05
    lon_uncer = .05
    mag_uncer = .1
    dep_uncer = 5
    time_uncer = 1
    version = 1
    timestamp = UTCDateTime.utcnow()

    lat = float(config['lat'])
    lon = float(config['lon'])
    dep = float(config['dep'])

    SA =  '<?xml version="1.0" encoding="UTF-8" standalone="no" ?>\n'
    SA += '<event_message alg_vers="3.1.4-2018-11-08" category="live" ' \
          'instance="epic@eew-bk-prod1" message_type="update" orig_sys="PDL" ref_id="0" ref_src="" ' \
          'timestamp="%s" version="%s">\n' % (timestamp, version)
    SA += '  <core_info id="%s">\n' % evid
    SA += '    <mag units="Mw">%f</mag>\n' % mag
    SA += '    <mag_uncer units="Mw">%f</mag_uncer>\n' % mag_uncer
    SA += '    <lat units="deg">%f</lat>\n' % lat
    SA += '    <lat_uncer units="deg">%f</lat_uncer>\n' % lat_uncer
    SA += '    <lon units="deg">%f</lon>\n' % lon
    SA += '    <lon_uncer units="deg">%f</lon_uncer>\n' % lon_uncer

    SA += '    <depth units="km">%f</depth>\n' % dep
    SA += '    <depth_uncer units="km">%f</depth_uncer>\n' % dep_uncer

    SA += '    <orig_time units="UTC">%s</orig_time>\n' % ot
    SA += '    <orig_time_uncer units="UTC">%s</orig_time_uncer>\n' % time_uncer
    #SA += '    <likelihood>1.0000</likelihood>\n'
    #SA += '    <num_stations>%d</num_stations>\n' % num_stations
    SA += '  </core_info>\n'
    SA += '</event_message>'

    return SA

if __name__ == "__main__":
    main()
