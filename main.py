import requests
import os
import sys
import time
from ruamel_yaml import YAML
import threading
import subprocess

yaml = YAML()
yaml.boolean_representation = ['False', 'True']


def enableLED():
    subprocess.Popen("./enableLED.sh")


def blinkSuccess():
    subprocess.Popen("./success.sh")


def blinkError():
    subprocess.Popen("./error.sh")


# load configuration
configPath = os.path.join(os.getcwd(), 'config.yaml')
configFile = open(configPath)
config = yaml.load(configFile)

config['ONLINE'] = True

# ###########
# Enable user control of pi led
enableLED()

# build request urls
serverURL = 'https://' + config['SERVER_IP'] + ':' + str(config['SERVER_PORT'])
initURL = serverURL + config['API_INIT']
dataURL = serverURL + config['API_DATA']
# header = {'Authorization': 'Bearer ' + config['API_TOKEN']}

# ####################
# Test and Initialize Connection with Server
def comInit():
    try:
        initReq = requests.post(initURL, auth=(config['TOKEN_ID'], config['API_TOKEN']),
                                json={'DEVICE_TYPE': config['DEVICE_TYPE'], 'TOKEN_ID': config['TOKEN_ID'],
                                      'DATA': 'init'})
    except Exception as e:
        print(f"Local Hub not found at {initURL}.  Raised Exception: {Exception}", file=sys.stdout)
        return False
    if not initReq.ok:
        print(f'Problem initializing with server.  Status Code {initReq.status_code}', file=sys.stdout)
        return False
    else:
        response = initReq.json()
        if 'DEVICE_ID' in response.keys():
            config['DEVICE_ID'] = response['DEVICE_ID']
            yaml.dump(config, configFile)


    return True


# ###########################
# Begin Main Code Loop


class IoControl(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        global commands
        global dataURL
        global config
        time.sleep(1)
        while config['ONLINE']:
            time.sleep(config['RATE'])
            try:
                commandRequest = requests.get(dataURL, auth=(config['TOKEN_ID'], config['API_TOKEN']))
                if commandRequest.ok:
                    commands = commandRequest.json()
                    print(f'Recieved commands: {commands}', file=sys.stdout)
                    if commands['RATE']:
                        config['RATE'] = commands['RATE']
                    if commands['STAY_ONLINE'] == 'False':
                        config['ONLINE'] = False
                        with open(configPath) as configFile:
                            yaml.dump(config, configFile)
            except:
                print('Warning: invalid/no commands received from server.', file=sys.stdout)
                blinkError()
        print('Shutdown command received- Stopping IO thread.', file=sys.stdout)


class SendStatus(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        global config
        while config['ONLINE']:
            time.sleep(config['RATE'])
            chirp = requests.post(dataURL, auth=(config['TOKEN_ID'], config['API_TOKEN']),
                                  json={'TOKEN_ID': config['TOKEN_ID'],
                                        'DEVICE_ID': config['DEVICE_ID'],
                                        'RATE': config['RATE']})
            if chirp.ok:
                print('Chirp sent successfully.', file=sys.stdout)
            else:
                print('Error sending chirp', file=sys.stdout)
                blinkError()
        print('Shutdown command received- Stopping chirp thread.', file=sys.stdout)


ioControl = IoControl()
sendStatus = SendStatus()

threads = [ioControl, sendStatus]

if comInit():
    blinkSuccess()
    for t in threads:
        t.start()

    for t in threads:
        t.join()
else:
    blinkError()
time.sleep(15)
# #####################
# Shutdown

print('Thread shutdown complete. Shutting down device...', file=sys.stdout)

subprocess.Popen(['shutdown', '-h', 'now'])
