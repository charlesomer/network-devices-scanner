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

    print("START")
    print("Checking for devices.")

    with open('/network-devices-scanner/devices.json') as json_file:
        data = json.load(json_file)
        for deviceMac in data:
            print("Scanning for " + data[deviceMac]['name'] + " (" + deviceMac + ") using IP address: " + data[deviceMac]['ip'])
            tempScan = nm.scan(data[deviceMac]['ip'])
            print("Scanned. Now get mac address of IP address " + data[deviceMac]['ip'])
            macAddressOfIPOnTheNetwork = get_mac_address(ip=data[deviceMac]['ip'])
            print("Done. Mac address for " + data[deviceMac]['ip'] + " is " + macAddressOfIPOnTheNetwork)
            if tempScan['nmap']['scanstats']['downhosts'] != '1' and macAddressOfIPOnTheNetwork == deviceMac:
                # This device is on the network and correct IP is stored in json.
                print(data[deviceMac]['name'] + " is on the network and the IP address is " + data[deviceMac]['ip'])
                isSomeoneHome = 1
            elif macAddressOfIPOnTheNetwork != deviceMac:
                print("Stored IP address for " + data[deviceMac]['name'] + " is incorrect and will be updated if available.")
                rescanNetwork = 1
            print()

    if rescanNetwork == 1:
        print("Need to update some IP address, scanning networking now...")
        with open('/network-devices-scanner/config.json') as json_file:
            dataFile = json.load(json_file)
            scan = nm.scan(dataFile['network'])
            print("Finished scanning network.")
            for scan_ip in scan['scan']:
                for deviceMac in data:
                    if get_mac_address(ip=scan_ip) == deviceMac:
                        print(data[deviceMac]['name'] + " is on the network with IP address " + scan_ip)
                        data[deviceMac]['ip'] = scan_ip
                        isSomeoneHome = 1
                        updateJsonFile = 1

    print()
    if updateJsonFile == 1:
        print("Updating JSON file.")
        with open('/network-devices-scanner/devices.json', 'w') as outfile:
            json.dump(data, outfile, indent=4)
            print("Updated JSON file.")
    else:
        print("JSON file does not need updating.")

    print()
    with open('/network-devices-scanner/config.json') as json_file:
        data = json.load(json_file)
        if isSomeoneHome == 1:
            print("One or more requested devices are on the network. Sending request...")
            requests.get(data['request-when-devices-are-home'])
            print("Request sent.")
        else:
            print("No requested devices are on the network. Sending request...")
            requests.get(data['request-when-devices-are-not-home'])
            print("Request sent.")

    print("END")
    print()

    s.enter(runEveryXSeconds, 1, checkForDevices, (sc,))

# Don't wait on first run.
s.enter(1, 1, checkForDevices, (s,))
s.run()
