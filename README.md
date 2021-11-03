# CCU Alarm

## Summary

The CCU Alarm tool is a powerful but simple alarm system for your CCU. It prevents you from writing huge scripts in the frontend which give you less detailed information about alarms.

Currently it supports the Homematic IP sensors HmIP-SMI (indoor motion sensor) and HMIP-SWDO (optical window/door sensor), which are recognized automatically. If the alarm system is enabled and an alarm is detected, one is notified via Cloudmatic Push and can create following programs in the CCU frontend using the AlarmDelay boolean variable.

## Prerequisites

This tool uses the CCU's XML API with disabled authentication. It can be installed as described here: https://github.com/homematic-community/XML-API

You need the following system variables in your CCU:
* Alarm (Type Werteliste, with values 'Unscharf; Huellschutz; Vollschutz')
* AlarmDelay (Type Logikwert)
* SmarthaPush (Type Zeichenkette, containing your Smartha API Key for push messages)

What you also need is some kind of program that sets the Alarm variable (=enables and disables the alarm system). I am using the hand sender device HmIP-KRC4 for this purpose.

## Usage

It is recommended to use the docker image:

The environment variable CCU_URL must point to the root of the XML API. Default value is ```https://homematic-raspi/addons/xmlapi```

```docker run -d --restart=unless-stopped --name=ccu-alarm -e CCU_URL=<url_to_you_xml_api> alexalex89/ccu-alarm:latest```