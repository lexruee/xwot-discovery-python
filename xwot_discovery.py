import zeroconf
from zeroconf import ServiceStateChange

import socket

class Resource:

    def __init__(self, name, urn, port = None, properties = {}, address = None):
        self.name = name
        self.urn = urn
        self.port = port
        self.address = address
        self.properties = properties


class Adapter(object):
    """A generic adapter interface for using different service discovery protocols."""

    def browse():
        raise NotImplementedError('Subclass should implement this!')

    def register(resource):
        raise NotImplementedError('Subclass should implement this!')

    def unregister(resource):
        raise NotImplementedError('Subclass should implement this!')

    def close():
        raise NotImplementedError('Subclass should implement this!')


""""
    Zeroconf Servcie Discovery Adapter Layer
"""

class ZeroconfListener(object):
    """
    A Zeroconf Listener provides an interface whose methods are called if
    1) a new service is discovered
    2) a service is removed
    3) status of a service has changed
    """

    def removeService(self, zeroconf, type, name):
            raise NotImplementedError('Subclass should implement this!')

    def addService(self, zeroconf, type, name):
            raise NotImplementedError('Subclass should implement this!')

    def onChange(self, zeroconf, type, name, state_change):
        raise NotImplementedError('Subclass should implement this!')

    def handle(self, zeroconf, service_type, name, state_change):
        if state_change is ServiceStateChange.Added:
            self.addService(zeroconf, service_type, name)
        elif state_change is ServiceStateChange.Removed:
            self.removeService(zeroconf, service_type, name)
        else:
            pass
        self.onChange(zeroconf, service_type, name, state_change)

class ZeroconfBrowser(ZeroconfListener):
    """
        A Zeroconf Browser implements a part of the Zeroconf Listener interface.
        It implements only the addService method which is called if a new service is
        discovered,
    """

    def __init__(self, callback):
        self.callback = callback

    def removeService(self, zeroconf, type, name):
        pass

    def addService(self, zeroconf, type, name):
        self.callback(zeroconf, type, name)

    def onChange(self, zeroconf, service_type, name, state_change):
        pass


class ZeroconfAdapter(Adapter):
    """An adapter for the zeroconf service."""

    TYPE = "_xwot._tcp.local."

    def __init__(self):
        self.zeroconfService = zeroconf.Zeroconf()
        self.services = []

    def register(self, resource):
        """Registers a resource."""

        address = socket.inet_aton("127.0.0.1")
        if resource.address != None:
            address = socket.inet_aton(resource.address)

        name = resource.name

        # fix
        if not resource.name.endswith(self.TYPE):
            name = resource.name + '.' + self.TYPE

        serviceInfo = zeroconf.ServiceInfo(type = self.TYPE,
                           name = name,
                           address = address,
                           port = resource.port,
                           properties = resource.properties)
        self.zeroconfService.register_service(serviceInfo)
        self.services.append([resource, serviceInfo])


    def unregister(self, resource):
        """Unregisters a resource."""

        removeServices = filter(lambda (resource, _): resource.name == resource.name, self.services)
        [ self.zeroconfService.unregister_service(serviceInfo) for (_, serviceInfo) in removeServices ]
        self.services = filter(lambda service: service not in removeServices, self.services)


    def browse(self, callback):
        """Browses the available xwot reources."""
        listener = ZeroconfBrowser(callback)
        zeroconf.ServiceBrowser(self.zeroconfService, self.TYPE, handlers = [listener.handle])


    def close(self):
        self.zeroconfService.close()



""""
    Simple Service Discovery Adapter Layer
"""

class SSDPAdapter(Adapter):
    pass



SERVICE = ZeroconfAdapter()

def service():
    """Returns a discover service object."""
    return SERVICE
