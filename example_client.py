import xwot_discovery
import socket
service = xwot_discovery.service()

def browse_callback(zeroconf, service_type, name):

    info = zeroconf.get_service_info(service_type, name)
    if info:
        print("  Address: %s:%d" % (socket.inet_ntoa(info.address), info.port))
        print("  Weight: %d, priority: %d" % (info.weight, info.priority))
        print("  Server: %s" % (info.server,))
        if info.properties:
            print("  Properties are:")
            for key, value in info.properties.items():
                print("    %s: %s" % (key, value))
        else:
            print("  No properties")
    else:
        print("  No info")
    print('\n')

service.browse(browse_callback)
try:
    while True:
        i = raw_input("Waiting (press Enter to exit)...\n\n")
        i = i.strip()
        if i == "r":
            service.browse(browse_callback)
        else:
            break
finally:
    service.close()
