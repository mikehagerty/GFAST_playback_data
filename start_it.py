import os
import argparse
from datetime import datetime, timezone
import glob
import sys
import yaml
import xml.etree.ElementTree as ET

GFAST_EVENTS_DIR = "../GFAST/events"

known_events = ['iquique', 'kaikoura', 'maule', 'nicoya', 'ridgecrest', 'anchorage', 'kumamoto', 'ibaraki']

def main():
    '''
        Simple script to modify playback event ShakeAlert SA.xml with time = now
        and start tankplayer to begin releasing tankplayer packets onto the wave_ring
    '''

    params_dir = os.environ.get('EW_PARAMS')
    cwd = os.getcwd()
    target_dir = os.path.join(cwd, GFAST_EVENTS_DIR)

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
    xmlfile = SAfile
    target = os.path.join(target_dir, os.path.basename(xmlfile))

    tree = ET.parse(xmlfile)
    root = tree.getroot()
    core = root.find('core_info')
    orig_time = core.find('orig_time')
    # The tankplayer will stamp the first packets to NOW
    #   So we adjust the OT by offset_time wrt actual first packet time:
    timestamp = datetime.now(tz=timezone.utc).timestamp()
    otime = datetime.utcfromtimestamp(timestamp).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    print("         Now time:%s   [%f]" % (otime, timestamp))
    timestamp = datetime.now(tz=timezone.utc).timestamp() + offset_time
    otime = datetime.utcfromtimestamp(timestamp).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    print("Stamp origin time:%s   [%f]" % (otime, timestamp))
    orig_time.text = orig_time.text.replace(orig_time.text, otime)

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


if __name__ == "__main__":
    main()
