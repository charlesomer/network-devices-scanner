import sched, time
import json
import nmap
import requests
from getmac import get_mac_address

s = sched.scheduler(time.time, time.sleep)
runEveryXSeconds = 60 * 10

def checkForDevices(sc):

    nm = nmap.PortScanner()
    data = None
    updateJsonFile = 0
    isSomeoneHome = 0
    rescanNetwork = 0

    print("Checking known IPs")

    with open('/network-devices-scanner/devices.json') as json_file:
        data = json.load(json_file)
        for deviceMac in data:
            print("Checking " + deviceMac
            tempScan = nm.scan(data[deviceMac]['ip'])
            macAddressOfIPOnTheNetwork = get_mac_address(ip=data[deviceMac]['ip'])
            if tempScan['nmap']['scanstats']['downhosts'] != '1' and macAddressOfIPOnTheNetwork == deviceMac:
                # This device is on the network.
                print(data[deviceMac]['name'] + " is on the network.")
                isSomeoneHome = 1

            if macAddressOfIPOnTheNetwork != deviceMac:
                rescanNetwork = 1

    if rescanNetwork == 1:
        print("Scanning network and updating json if need be.")
        scan = nm.scan('192.168.0.0/24')
        for scan_ip in scan['scan']:
            for deviceMac in data:
                if get_mac_address(ip=scan_ip) == deviceMac:
                    data[deviceMac]['ip'] = scan_ip
                    isSomeoneHome = 1
                    updateJsonFile = 1

    if updateJsonFile == 1:
        with open('/network-devices-scanner/devices.json', 'w') as outfile:
            json.dump(data, outfile, indent=4)
            print("Updating JSON")

    with open('/network-devices-scanner/config.json') as json_file:
        if isSomeoneHome == 1:
            requests.get(json_file['request-when-devices-are-home'])
            print("Devices are home.")
        else:
            requests.get(json_file['request-when-devices-are-not-home'])
            print("Devices are not home.")

    s.enter(runEveryXSeconds, 1, checkForDevices, (sc,))

# Don't wait on first run.
s.enter(1, 1, checkForDevices, (s,))
s.run()
