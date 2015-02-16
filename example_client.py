import xwot_discovery
import socket
service = xwot_discovery.service()

def browse_callback(resource):
    # urn =  resource.urn()
    # name = resource.name()
    # port = resource.port()
    # address = resource.address()
    properties = resource.properties()

    print "resource:"
    print "\n".join([ "%s : %s" % (k,v) for k,v in properties.items() ])
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
