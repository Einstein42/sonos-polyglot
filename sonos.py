#!/usr/bin/python
""" Sonos Node Server for Polyglot 
      by Einstein.42(James Milne)
      milne.james@gmail.com"""

from polyglot.nodeserver_api import SimpleNodeServer, PolyglotConnector
from sonos_types import SonosSpeaker, SonosControl

VERSION = "0.1.1"


class SonosNodeServer(SimpleNodeServer):
    """ Sonos Node Server """
    controller = []
    speakers = []

    def setup(self):
        manifest = self.config.get('manifest',{})
        self.controller = SonosControl(self,'sonoscontrol','Sonos Control', True, manifest)
        self.poly.LOGGER.info("FROM Poly ISYVER: " + self.poly.isyver)
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
        
def main():
    # Setup connection, node server, and nodes
    poly = PolyglotConnector()
    # Override shortpoll and longpoll timers to 5/30, once per second in unnessesary 
    nserver = SonosNodeServer(poly, 5, 30)
    poly.connect()
    poly.wait_for_config()
    poly.LOGGER.info("Sonos Interface version " + VERSION + " created. Initiating setup.")
    nserver.setup()
    poly.LOGGER.info("Setup completed. Running Server.")
    nserver.run()
    
if __name__ == "__main__":
    main()
