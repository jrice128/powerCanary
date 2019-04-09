import requests
import os
import time
from ruamel_yaml import YAML
import threading
import subprocess

yaml = YAML()

def enableLED():
    subprocess.run("./enableLED.sh")
def blinkSuccess():
    subprocess.run("./success.sh")
def blinkError():
    subprocess.run("./error.shpytho")

# load configuration
configPath = os.path.join(os.getcwd(), 'config.yaml')
with open(configPath) as configFile:
    try:
        config = yaml.load(configFile, Loader=yaml.FullLoader)
    except yaml.YAMLError as exc:
        raise FileNotFoundError(exc)

# ###########
# Enable user control of pi led
enableLED()

# build request urls
serverURL = 'https://' + config['SERVER_IP'] + ':' + config['SERVER_PORT']
initURL = serverURL + config['API_INIT']
dataURL = serverURL + config['API_DATA']


s = requests.session()

# Attempt to connect to local hub
try:
    initReq = s.post(initURL, json={'API_TOKEN': config['API_TOKEN'], 'DEVICE_TYPE': config['DEVICE_TYPE']})
except Exception as e:
    raise ConnectionError(f"Local Hub not found at {initURL}.  Raised Exception: {Exception}")

if initReq.status_code != 200:
    raise ConnectionError(f'Problem initializing with server.  Status Code {initReq.status_code}')


# #################
# Begin Loop main code


class ioControl(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        global commands
        global dataURL
        global config
        while commands['STAY_ONLINE']:
            try:
                commands = requests.get(dataURL, auth=config['API_TOKEN'])  # TODO Check on proper credential sending
            except:
                continue



class sendStatus(threading.Thread):
    def __init__(self, image):
        threading.Thread.__init__(self)
        self.image = image

    def run(self):
        global config
        try:
            requests.post(dataURL, data=self.image) #Todo check how to post file
        except:
            pass


