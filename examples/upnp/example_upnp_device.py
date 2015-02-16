# Licensed under the MIT license
# http://opensource.org/licenses/mit-license.php or see LICENSE file.
# Copyright 2007-2009 Brisa Team <brisa-develop@garage.maemo.org>
import time
from brisa.core.reactors import install_default_reactor
reactor = install_default_reactor()

import os
import threading

from brisa.upnp.device import Device, Service


class SwitchPower(Service):

    def __init__(self):
        Service.__init__(self,
                         'SwitchPower',
                         'urn:schemas-upnp-org:service:SwitchPower:1',
                         '',
                         os.getcwd() + '/SwitchPower-scpd.xml')
        self.target = False
        self.status = False

    def SetTarget(self, *args, **kwargs):
        self.target = kwargs['NewTargetValue']
        self.status = self.target
        print 'Light switched ', {'1': 'on', '0': 'off'}.get(self.target, None)
        return {}

    def GetTarget(self, *args, **kwargs):
        return {'RetTargetValue': self.target}

    def soap_GetStatus(self, *args, **kwargs):
        return {'ResultStatus': self.status}

def main_loop(device):
    reactor.add_after_stop_func(device.stop)
    reactor.main()

if __name__ == '__main__':
    device = Device('urn:schemas-upnp-org:device:BinaryLight:1','Binary Light device')
    device += SwitchPower()
    # Start device
    device.start()
    # Setup main loop
    threading.Thread(target=main_loop)
    while True:
        time.sleep(2)
        device.SSDP.announce_device()
