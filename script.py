import sched, time
import json
import nmap3
import requests
import os
import copy
from datetime import datetime, timedelta
from getmac import get_mac_address

s = sched.scheduler(time.time, time.sleep)

def checkForDevices(sc):

    print("START at " + datetime.now().strftime("%Y-%m-%d %H:%M"))
    print("Checking for devices.")

    directoryPath = os.path.dirname(os.path.abspath('./config-files/config.json'))
    devicesJSONFilePath = directoryPath + '/devices.json'
    configJSONFilePath = directoryPath + '/config.json'

    # Open files.
    with open(devicesJSONFilePath) as json_file:
        devicesJSON = json.load(json_file)
    with open(configJSONFilePath) as json_file:
        configJSON = json.load(json_file)

    # Set vars.
    nmap = nmap3.Nmap()
    devicesJSONOriginal = copy.deepcopy(devicesJSON)
    sendAwayRequest = True # Assume no one is home until shown otherwise.
    rescanNetwork = False
    minutesBetweenScans = int(configJSON['minutes-between-scans'])
    minutesToWaitForDeviceToReturn = int(configJSON['minutes-to-wait-for-device-to-return'])
    usingCronInstead = bool(configJSON['using-cron-instead'])

    # Loop through all devices in devices.json.
    for deviceMac in devicesJSON:
        if (datetime.now() - timedelta(minutes=minutesToWaitForDeviceToReturn)) < datetime.strptime(devicesJSON[deviceMac]['lastSeen'], "%Y-%m-%d %H:%M"):
            sendAwayRequest = False
            print(devicesJSON[deviceMac]['name'] + " has been on the network in the last " + str(minutesToWaitForDeviceToReturn) + " minutes.")
        else:
            print(devicesJSON[deviceMac]['name'] + " has not been on the network in the last " + str(minutesToWaitForDeviceToReturn) + " minutes.")

        print("Scanning for " + devicesJSON[deviceMac]['name'] + " (" + deviceMac + ") using IP address: " + devicesJSON[deviceMac]['ip'])
        tempScan = nmap.scan_top_ports(devicesJSON[deviceMac]['ip'])
        print("Scanned.")
        if devicesJSON[deviceMac]['ip'] in tempScan:
            print("Now get mac address of IP address " + devicesJSON[deviceMac]['ip'])
            macAddressOfIPOnTheNetwork = get_mac_address(ip=devicesJSON[deviceMac]['ip']).upper()
            if macAddressOfIPOnTheNetwork != None:
                print("Done. Mac address for " + devicesJSON[deviceMac]['ip'] + " is " + macAddressOfIPOnTheNetwork)
                if macAddressOfIPOnTheNetwork == deviceMac:
                    # This device is on the network and correct IP is stored in json.
                    print(devicesJSON[deviceMac]['name'] + " is on the network and the IP address is " + devicesJSON[deviceMac]['ip'])
                    devicesJSON[deviceMac]['lastSeen'] = datetime.now().strftime("%Y-%m-%d %H:%M")
                    sendAwayRequest = False
                elif macAddressOfIPOnTheNetwork != deviceMac:
                    print("Stored IP address for " + devicesJSON[deviceMac]['name'] + " is incorrect and will be updated if available.")
                    rescanNetwork = True
            else:
                print("Done. No device exists at IP address " + devicesJSON[deviceMac]['ip'] + ". JSON will be updated.")
                rescanNetwork = True
        else:
            print("IP address is not on the network, rescan to check if it's changed and to determine if device is on network still.")
            rescanNetwork = True
        print()

    if rescanNetwork == True:
        print("Need to update some IP address, scanning networking now...")
        scan = nmap.scan_top_ports(configJSON['network'])
        print("Finished scanning network.")
        for scan_ip in scan:
            for deviceMac in devicesJSON:
                themac = get_mac_address(ip=scan_ip)
                if themac != None and themac.upper() == deviceMac:
                    print(devicesJSON[deviceMac]['name'] + " is on the network with IP address " + scan_ip)
                    sendAwayRequest = False
                    devicesJSON[deviceMac]['ip'] = scan_ip
                    devicesJSON[deviceMac]['lastSeen'] = datetime.now().strftime("%Y-%m-%d %H:%M")

    print()
    if devicesJSON != devicesJSONOriginal:
        print("Updating JSON file.")
        with open(configJSONFilePath, 'w') as outfile:
            json.dump(devicesJSON, outfile, indent=4)
            print("Updated JSON file.")
    else:
        print("JSON file does not need updating.")

    print()
    if sendAwayRequest == False:
        print("One or more requested devices are on the network. Sending request...")
        requests.get(configJSON['request-when-devices-are-home'])
        print("Request sent.")
    else:
        print("No requested devices are on the network. Sending request...")
        requests.get(configJSON['request-when-devices-are-not-home'])
        print("Request sent.")

    print("END")
    print()

    if usingCronInstead != True:
        s.enter(minutesBetweenScans * 60, 1, checkForDevices, (sc,))

# Don't wait on first run.
s.enter(1, 1, checkForDevices, (s,))
s.run()
