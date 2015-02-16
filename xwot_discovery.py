
class Resource:
    """ Data container for resource objects. """

    def __init__(self, name, urn, location, properties = {}, address = None, port = None, info = {}):
        self._name = name
        self._port = port
        self._address = address
        self._info = info
        self._properties = properties
        self._properties['location'] = location
        self._properties['name'] = name
        self._properties['urn'] = urn

    def properties(self):
        return self._properties

    def port(self):
        return self._port

    def address(self):
        return self._address

    def info(self):
        return self._info

    def urn(self):
        return self._properties['urn']

    def name(self):
        return self._properties['name']

    def location(self):
        return self._properties['location']


""""
    A discover adapter for different discovery protocol implementations.
"""
class DiscoveryAdapter(object):
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
import zeroconf
from zeroconf import ServiceStateChange
import socket

class ZeroconfListener(object):
    """
    A Zeroconf Listener provides an interface whose methods are called if
    1) a new service is discovered
    2) a service is removed
    3) status of a service has changed
    """


    def removeService(self, service, stype, name):
        raise NotImplementedError('Subclass should implement this!')


    def addService(self, service, stype, name):
        raise NotImplementedError('Subclass should implement this!')


    def onChange(self, service, stype, name, state_change):
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


    def _createResource(self, zeroconf, service_type, name):
        info = zeroconf.get_service_info(service_type, name)
        address, port = socket.inet_ntoa(info.address), info.port
        properties = dict(info.properties) # copy dict

        return Resource(name = properties['name'],
                urn = properties['urn'],
                port = port,
                address = address,
                properties = properties,
                location = properties['location'],
                info = info)


    def removeService(self, service, stype, name):
        pass


    def addService(self, service, stype, name):
        resource = self._createResource(service, stype, name)
        self.callback(resource)


    def onChange(self, *args):
        pass


class ZeroconfAdapter(DiscoveryAdapter):
    """An adapter for the zeroconf service."""

    TYPE = "_xwot._tcp.local."

    def __init__(self):
        self.zeroconfService = zeroconf.Zeroconf()
        self.services = []


    def register(self, resource):
        """Registers a resource."""

        address = socket.inet_aton("127.0.0.1")
        if resource.address() != None:
            address = socket.inet_aton(resource.address())

        name = resource.name()

        # fix
        if not resource.name().endswith(self.TYPE):
            name = resource.name() + '.' + self.TYPE

        serviceInfo = zeroconf.ServiceInfo(type = self.TYPE,
                           name = name,
                           address = address,
                           port = resource.port(),
                           properties = resource.properties())
        self.zeroconfService.register_service(serviceInfo)
        self.services.append([resource, serviceInfo])


    def unregister(self, resource):
        """Unregisters a resource."""

        removeServices = filter(lambda (res, _): res.name() == resource.name(), self.services)
        [ self.zeroconfService.unregister_service(serviceInfo) for (_, serviceInfo) in removeServices ]
        self.services = filter(lambda service: service not in removeServices, self.services)


    def browse(self, callback):
        """Browses the available xwot reources."""
        # wrap callback into a ZeroconfBrowser
        listener = ZeroconfBrowser(callback)
        zeroconf.ServiceBrowser(self.zeroconfService, self.TYPE, handlers = [listener.handle])


    def close(self):
        [ self.zeroconfService.unregister_service(serviceInfo) for (_, serviceInfo) in self.services ]
        self.zeroconfService.close()


SERVICE = {
    'zeroconf' : ZeroconfAdapter()
}


def service(protocol = 'zeroconf'):
    """Returns a discovery service object."""
    service = SERVICE[protocol]

    if service == None:
        raise 'Error!'

    return service
