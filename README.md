# network-devices-scanner
Scans the network for specified MAC addresses and sends IFTTT request if they do or do not exist.

Originally developed to switch away mode on/off for Wiser Smart Heating software (which supports IFTTT). Could be useful for more smart heating systems.

Install the requirements, create the required files and run `script.py`.

Was unable to get nmap to work correctly via docker, see `docker-compose.yaml` for an example docker compose config I have tried. If anyone manages to get this to work please let me know.

Scans every 5 minutes and if no devices have been seen after 15 minutes, send request. This can be changed in config.json as well as other details.

Could do with some cleaning up.