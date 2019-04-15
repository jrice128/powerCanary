import requests
import os
import sys
import time
from ruamel_yaml import YAML
import threading
import subprocess

yaml = YAML()


def enableLED():
    subprocess.Popen("./enableLED.sh")


def blinkSuccess():
    subprocess.Popen("./success.sh")


def blinkError():
    subprocess.Popen("./error.sh")


# load configuration
configPath = os.path.join(os.getcwd(), 'config.yaml')
with open(configPath) as configFile:
    try:
        config = yaml.load(configFile, Loader=yaml.FullLoader)
    except yaml.YAMLError as exc:
        raise FileNotFoundError(exc)

config['ONLINE'] = True

# ###########
# Enable user control of pi led
# enableLED()

# build request urls
serverURL = 'http://' + config['SERVER_IP'] + ':' + config['SERVER_PORT'] # ToDo convert to HTTPS after testing
initURL = serverURL + config['API_INIT']
dataURL = serverURL + config['API_DATA']
header = {'Authorization': 'Bearer ' + config['API_TOKEN']}


# Attempt to connect to local hub
def comInit():
    try:
        initReq = requests.post(initURL, headers=header, json={'DEVICE_TYPE': config['DEVICE_TYPE'],
                                                              'DEVICE_ID': config['DEVICE_ID'],
                                                              'DATA': 'init'})
    except Exception as e:
        print(f"Local Hub not found at {initURL}.  Raised Exception: {Exception}", file=sys.stdout)
        return False
    if not initReq.ok:
        print(f'Problem initializing with server.  Status Code {initReq.status_code}', file=sys.stdout)
        return False
    return True

# #################
# Begin Loop main code


class IoControl(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        global commands
        global dataURL
        global config
        while config['ONLINE']:
            try:
                commandRequest = requests.get(dataURL, headers=header)
                commands = commandRequest.json()
                if commands['RATE']:
                    config['RATE'] = commands['RATE']
                if commands['STAY_ONLINE'] == 'False':
                    config['ONLINE'] = False
                    # with open(configPath) as configFile:
                    #     yaml.dump(config, configFile)
            except:
                print('Warning: no commands received from server.', file=sys.stdout)
        print('Shutdown command received- Stopping IO thread.', file=sys.stdout)


class SendStatus(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        global config
        while config['ONLINE']:
            time.sleep(config)
            chirp = requests.post(dataURL, headers=header, json={'DEVICE_ID': config['DEVICE_ID'],
                                                                 'RATE': config['RATE']})
            if chirp.ok:
                print('Chirp sent successfully.', file=sys.stdout)
            else:
                print('Error sending chirp', file=sys.stdout)
        print('Shutdown command received- Stopping chirp thread.', file=sys.stdout)


ioControl = IoControl()
sendStatus = SendStatus()

threads = [ioControl, sendStatus]

for t in threads:
    t.start()

for t in threads:
    t.join()


# #####################
# Shutdown

print('Thread shutdown complete. Shutting down device...', file=sys.stdout)

# subprocess.Popen(['shutdown', '-h', 'now'])
