import os
import argparse
from datetime import datetime, timezone
import glob
import sys
import yaml
import xml.etree.ElementTree as ET

from obspy.core.utcdatetime import UTCDateTime

#GFAST_EVENTS_DIR = "../GFAST/events"
GFAST_DIR = "./run"

#known_events = ['iquique', 'kaikoura', 'maule', 'nicoya', 'ridgecrest', 'anchorage', 'kumamoto', 'ibaraki']
known_events = []
for event in glob.glob('test_data/*'):
    known_events.append(os.path.basename(event))

print(known_events)

def main():
    '''
        Simple script to modify playback event ShakeAlert SA.xml with time = now
        and start tankplayer to begin releasing tankplayer packets onto the wave_ring
    '''

    params_dir = os.environ.get('EW_PARAMS')
    cwd = os.getcwd()

    if params_dir is None:
        print("You must source an EW env before running this!")
        exit(2)

    usage = "python start_it.py kaikoura (or some other event in known_events)"
    if len(sys.argv) != 2 or sys.argv[1] not in known_events:
        print(usage)
        exit(2)

    event = sys.argv[1]
    event_path = os.path.join('test_data', event)
    configFile = os.path.join(event_path, 'config.yml')

    configuration = {}
    with open(configFile, 'r') as ymlfile:
        config = yaml.load(ymlfile, Loader=yaml.FullLoader)

    try:
        offset_time = float(config['offset_time'])
        tankfile = config['tankfile']
        SAfile = os.path.join(event_path, os.path.basename(config['SA_file']))
    except:
        raise

    # Where SA.xml file will be dropped:
    target_dir = os.path.join(GFAST_DIR, os.path.join(event, 'events'))

    # Copy tankplayer.d template to EW_PARAMS/tankplayer.d.gfast with WaveFile set to find this tankfile
    path = os.path.join(cwd, event)
    tankfile = os.path.join(path, tankfile)

    tankplayer_file = os.path.join(params_dir, 'tankplayer.d.gfast')

    template = 'resources/tankplayer.d.template'
    lines = None
    with open(template, 'r') as f:
        lines = f.readlines()
    for i, line in enumerate(lines):
        if line[0:8] == 'WaveFile':
            lines[i] = line.replace('WaveFile', 'WaveFile %s' % tankfile)

    with open(tankplayer_file, 'w') as f:
        #f.write("%s" % lines)
        for line in lines:
            #f.write("{0}\n".format(line))
            f.write(line)


    # Modify the SA.xml file and drop it in the GFAST events dir
    '''
    xmlfile = SAfile
    target = os.path.join(target_dir, os.path.basename(xmlfile))

    tree = ET.parse(xmlfile)
    root = tree.getroot()
    core = root.find('core_info')
    orig_time = core.find('orig_time')
    '''
    # The tankplayer will stamp the first packets to NOW
    #   So we adjust the OT by offset_time wrt actual first packet time:
    #timestamp = datetime.now(tz=timezone.utc).timestamp()
    #otime = datetime.utcfromtimestamp(timestamp).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    #print("         Now time:%s   [%f]" % (otime, timestamp))
    #timestamp = datetime.now(tz=timezone.utc).timestamp() + offset_time
    timestamp = UTCDateTime.utcnow()
    otime = UTCDateTime.utcnow() + offset_time
    print("         Now time:%s" % timestamp)
    print("Stamp origin time:%s" % otime)
    #orig_time.text = orig_time.text.replace(orig_time.text, otime)
    SA = make_SA(config, otime)
    SA_file = os.path.join(target_dir, 'SA.xml')
    with open(SA_file, 'w') as f:
        f.write(SA)
    print(SA)
    exit()

    #print("chdir to:%s and look for tankfile:%s" % (params_dir, tankfile))
    #print(os.path.join(params_dir, tankfile))
    #os.chdir(params_dir)

    # Start tankplayer
    thread = myThread(1, "Thread-1", 1, tankfile)
    thread.start()

    #os.chdir(cwd)
    #target = os.path.join(xmldir_out, os.path.basename(xmlfile))

    time.sleep(30)
    tree.write(target)

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

    lat = config['lat']
    lon = config['lon']
    dep = config['dep']

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
