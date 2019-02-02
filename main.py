import sys
from device import Device

if len(sys.argv) < 4:
    print("Usage: main.py <ip> <port> <description_file_name>")
    sys.exit(0)

# TODO: sanitize input
ip = sys.argv[1]
port = sys.argv[2]
desc = '/' + sys.argv[3]
host = 'http://' + ip + ':' + port

device = Device(host, desc)
#device = Device('http://10.0.0.141:9197', '/dmr')
