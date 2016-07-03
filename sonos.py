#!/usr/bin/python
""" Sonos Node Server for Polyglot 
      by Einstein.42(James Milne)
      milne.james@gmail.com"""

from polyglot.nodeserver_api import SimpleNodeServer, PolyglotConnector
from sonos_types import SonosSpeaker, SonosControl

VERSION = "0.2.1"


class SonosNodeServer(SimpleNodeServer):
    """ Sonos Node Server """
    controller = []
    speakers = []

    def setup(self):
        super(SimpleNodeServer, self).setup()
        manifest = self.config.get('manifest',{})
        self.controller = SonosControl(self,'sonoscontrol','Sonos Control', True, manifest)
        self.poly.logger.info("FROM Poly ISYVER: " + self.poly.isyver)
        self.controller._discover()
        self.update_config()
        
    def poll(self):
        if len(self.speakers) >= 1:
            for i in self.speakers:
                i.update_info()
        pass

    def long_poll(self):
        # Future stuff
        pass

    def report_drivers(self):
        if len(self.speakers) >= 1:
            for i in self.speakers:
                i.report_driver()
        
def main():
    # Setup connection, node server, and nodes
    poly = PolyglotConnector()
    # Override shortpoll and longpoll timers to 5/30, once per second in unnessesary 
    nserver = SonosNodeServer(poly, 5, 30)
    poly.connect()
    poly.wait_for_config()
    poly.logger.info("Sonos Interface version " + VERSION + " created. Initiating setup.")
    nserver.setup()
    poly.logger.info("Setup completed. Running Server.")
    nserver.run()
    
if __name__ == "__main__":
    main()
