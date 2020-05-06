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

    with open('/devices.json') as json_file:
        data = json.load(json_file)
        for device in data:
            print("Checking " + data[device]['mac'])
            tempScan = nm.scan(data[device]['ip'])
            macAddressOfIPOnTheNetwork = get_mac_address(ip=data[device]['ip'])
            if tempScan['nmap']['scanstats']['downhosts'] != '1' and macAddressOfIPOnTheNetwork == device['mac']:
                # This device is on the network.
                print(data[device]['name'] + " is on the network.")
                isSomeoneHome = 1

            if macAddressOfIPOnTheNetwork != data[device]['mac']:
                rescanNetwork = 1

    if rescanNetwork == 1:
        print("Scanning network and updating json if need be.")
        scan = nm.scan('192.168.0.0/24')
        for scan_ip in scan['scan']:
            for device in data:
                if get_mac_address(ip=scan_ip) == data[device]['mac']:
                    data[device]['ip'] = scan_ip
                    isSomeoneHome = 1
                    updateJsonFile = 1

    if updateJsonFile == 1:
        with open('/devices.json', 'w') as outfile:
            json.dump(data, outfile, indent=4)
            print("Updating JSON")

    with open('/config.json') as json_file:
        if isSomeoneHome == 1:
            requests.get(json_file['request-when-devices-are-home'])
            print("Devices are home.")
        else:
            requests.get(json_file['request-when-devices-are-not-home'])
            print("Devices are not home.")

    s.enter(runEveryXSeconds, 1, checkForDevices, (sc,))

s.enter(runEveryXSeconds, 1, checkForDevices, (s,))
s.run()
