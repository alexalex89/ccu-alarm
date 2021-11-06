# CCU Alarm

## Summary

The CCU Alarm tool is a powerful but simple alarm system for your CCU. It prevents you from writing huge scripts in the frontend which give you less detailed information about alarms.

Main features:
* Alarm via Smartha push message on one or multiple devices
* Detailed alarm information (sensor name)
* Check if all sensors are not in alarm mode when activated (activation of motion sensors is delayed by two minutes)
* Send push message if Alarm state changes
* Supports the Homematic IP sensors HmIP-SMI (indoor motion sensor) and HMIP-SWDO (optical window/door sensor)
* Devices are recognized automatically
* Ability to create following programs in the CCU frontend using the AlarmDelay boolean variable.
* Push message if sabotage or low battery is detected

## Prerequisites

This tool uses the CCU's XML API with disabled authentication. It can be installed as described here: https://github.com/homematic-community/XML-API

You need the following system variables in your CCU:
* Alarm (Type Werteliste, with values 'Unscharf; Huellschutz; Vollschutz')
* AlarmDelay (Type Logikwert)
* SmarthaPush (Type Zeichenkette, containing your Smartha API Key for push messages)
    * Multiple variables with different API Keys are supported, they just have to start with "SmarthaPush"

What you also need is some kind of program that sets the Alarm variable (=enables and disables the alarm system). I am using the hand sender device HmIP-KRC4 for this purpose.

## Usage

It is recommended to use the docker image:

The environment variable CCU_URL must point to the root of the XML API. Default value is ```https://homematic-raspi/addons/xmlapi```

```docker run -d --restart=unless-stopped --name=ccu-alarm -e CCU_URL=<url_to_you_xml_api> alexalex89/ccu-alarm:latest```