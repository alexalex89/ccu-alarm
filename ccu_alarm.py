from lxml import etree
from models import sensors, status

import collections
import os
import requests
import time
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


URL = os.environ["CCU_URL"]


def init_devices(device_types=("HmIP-SMI", "HMIP-SWDO")):
    resp = requests.get(f"{URL}/devicelist.cgi", verify=False)
    devices = etree.fromstring(resp.text.encode())
    device_map = collections.defaultdict(list)
    for device in devices.xpath("/deviceList/device"):
        if device.get("device_type") in device_types:
            device_map[device.get("device_type")].append(device.get("ise_id"))
    return device_map


def send_push(message, api_keys, subject="ALARM"):
    for api_key in api_keys:
        requests.post("https://www.meine-homematic.de/prowlv3.php",
                      data={"id": 57913,
                            "key": "s10m20s27k68e95y59",
                            "apikey": api_keys,
                            "event": subject,
                            "pushtext": message.replace(" ", "+")},
                      verify=False).raise_for_status()


devices = init_devices()
state = {}
last_alarm_status = status.AlarmStatus.UNSCHARF


while True:
    resp = requests.get(f"{URL}/sysvarlist.cgi", verify=False)
    sys_vars = etree.fromstring(resp.text.encode())
    alarm_status = status.AlarmStatus.from_id(int(sys_vars.xpath("/systemVariables/systemVariable[@name='Alarm']")[0].get("value")))
    alarm_status_ise = sys_vars.xpath("/systemVariables/systemVariable[@name='Alarm']")[0].get("ise_id")
    alarm_delay_ise = sys_vars.xpath("/systemVariables/systemVariable[@name='AlarmDelay']")[0].get("ise_id")
    api_keys = []
    for var in sys_vars.xpath("/systemVariables/systemVariable"):
        if var.get("name", "").startswith("SmarthaPush"):
            api_keys.append(var.get("value"))

    if alarm_status != last_alarm_status:
        if alarm_status == status.AlarmStatus.HUELLSCHUTZ:
            send_push("Huellschutz aktiviert!", api_keys)
        elif alarm_status == status.AlarmStatus.VOLLSCHUTZ:
            time.sleep(120)
            send_push("Vollschutz aktiviert!", api_keys)
        elif alarm_status == status.AlarmStatus.UNSCHARF:
            requests.get(f"{URL}/statechange.cgi?ise_id={alarm_delay_ise}&new_value=false", verify=False)
            send_push("Alarm deaktiviert!", api_keys)
        last_alarm_status = alarm_status

    if alarm_status == status.AlarmStatus.UNSCHARF:
        print("Disabled.")
        state = {}
        time.sleep(15)
        continue

    print("Next iteration")
    for device_type, device_ids in devices.items():
        error = False
        resp = requests.get(f"{URL}/state.cgi?device_id={','.join(device_ids)}", verify=False)
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
                send_push(message=dev.name, api_keys=api_keys)
                requests.get(f"{URL}/statechange.cgi?ise_id={alarm_delay_ise}&new_value=true", verify=False)
                print(f"!!!ALARM {dev.name}!!!")
            if (ise_id in state and not state[ise_id].low_bat and dev.low_bat) or dev.low_bat:
                send_push(message=f"Device {dev.name} has low battery!", api_keys=api_keys)
            if ise_id in state and not state[ise_id].sabotage(alarm_status) and dev.sabotage(alarm_status):
                send_push(message=f"Sensor {dev.name} is sabotated!", api_keys=api_keys)
            if ise_id not in state and dev.check(alarm_status):
                # Protection activated but one sensor is already in alarm mode! Disable protection and send warning
                send_push(message=f"Cannot activate protection! {dev.name} already alarming!", api_keys=api_keys)
                requests.get(f"{URL}/statechange.cgi?ise_id={alarm_status_ise}&new_value=0", verify=False)
                error = True
                break
            state[ise_id] = dev
        if error:
            break
    time.sleep(5)
