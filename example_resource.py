import xwot_discovery
from xwot_discovery import Resource
from random import randint

service = xwot_discovery.service()
properties = {
    'room' : 'A 403'
}
resource = Resource(name = "lightswitch-%s" % randint(0,100),
                    urn = 'urn:xwot:lightswitch',
                    location = 'http://10.0.0.34/temperature-sensor',
                    port = 80,
                    properties = properties)

service.register(resource)

try:
    raw_input("Waiting (press Enter to exit)...\n\n")
finally:
    service.unregister(resource)
    service.close()
