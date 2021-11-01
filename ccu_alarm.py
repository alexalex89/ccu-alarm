from lxml import etree
from models import sensors, status
from urllib.parse import urlencode

import collections
import json
import os
import requests
import time
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


URL = "https://homematic-raspi/addons/xmlapi"
APIKEY = "CM%2d40EABA6B%2d634A%2d4698%2d9E47%2d0F3FABC37C81"


def init_devices(device_types=("HmIP-SMI", "HMIP-SWDO")):
    resp = requests.get(f"{URL}/devicelist.cgi", verify=False)
    devices = etree.fromstring(resp.text.encode())
    device_map = collections.defaultdict(list)
    for device in devices.xpath("/deviceList/device"):
        if device.get("device_type") in device_types:
            device_map[device.get("device_type")].append(device.get("ise_id"))
    return device_map


# devices = init_devices()
# with open(os.path.join(os.path.dirname(__file__), "devices.json"), "w") as f_devices:
#     json.dump(devices, f_devices)
with open(os.path.join(os.path.dirname(__file__), "devices.json"), "r") as f_devices:
    devices = json.load(f_devices)


def send_push(message, subject="ALARM"):
    requests.post("https://www.meine-homematic.de/prowlv3.php",
                  data={"id": 57913,
                        "key": "s10m20s27k68e95y59",
                        "apikey": APIKEY,
                        "event": subject,
                        "pushtext": message},
                  verify=False).raise_for_status()


state = {}


while True:
    resp = requests.get(f"{URL}/sysvarlist.cgi", verify=False)
    sys_vars = etree.fromstring(resp.text.encode())
    alarm_status = status.AlarmStatus.from_id(int(sys_vars.xpath("/systemVariables/systemVariable[@name='Alarm']")[0].get("value")))

    if alarm_status == status.AlarmStatus.UNSCHARF:
        print("Disabled.")
        time.sleep(15)
        continue

    print("Next iteration")
    for device_type, device_ids in devices.items():
        resp = requests.get(f"{URL}//state.cgi?device_id={','.join(device_ids)}", verify=False)
        device_list = etree.fromstring(resp.text.encode("latin1"))
        for device in device_list.xpath("/state/device"):
            if device_type == "HmIP-SMI":
                dev = sensors.HMIPSMI(device)
            elif device_type == "HMIP-SWDO":
                dev = sensors.HMIPSWDO(device)
            else:
                continue

            ise_id = dev.ise_id
            if ise_id in state and not state[ise_id].check(alarm_status) and dev.check(alarm_status):
                send_push(message=dev.name.replace(" ", "+"))
                print(f"!!!ALARM {dev.name}!!!")
            state[ise_id] = dev
    time.sleep(5)
