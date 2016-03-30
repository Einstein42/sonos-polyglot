#!/usr/bin/python
""" Sonos Node Server for Polyglot """

from polyglot.nodeserver_api import SimpleNodeServer, PolyglotConnector
from sonos_types import SonosSpeaker, SonosControl

VERSION = "0.0.1"


class SonosNodeServer(SimpleNodeServer):
    """ Sonos Node Server """
    speakers = []

    def setup(self):
        manifest = self.config.get('manifest',{})
        SonosControl(self,'sonoscontrol','Sonos Control', True, manifest)
        self.update_config()
        self.poly.LOGGER.info("FROM Poly ISYVER: " + self.poly.isyver)
        self.long_poll()
        
    def poll(self):
        if self.speakers.count >= 1:
            for i in self.speakers:
                i.update_info()
        return

    def long_poll(self):
        """
        manifest = self.config.get('manifest',{})
        speakers = soco.discover()
        for speaker in speakers:
            try:
                manifest[speaker.uid[8:22]]['ip_address'] = speaker.ip_address
                self.poly.LOGGER.info("Manifest: " + str(manifest))
            except KeyError as e:
                self.poly.LOGGER.error("KeyError: %s", e)
        """
        return
        
def main():
    """ setup connection, node server, and nodes """
    poly = PolyglotConnector()
    nserver = SonosNodeServer(poly, 5, 30)
    poly.connect()
    poly.wait_for_config()
    poly.LOGGER.info("Sonos Interface version " + VERSION + " created. Initiating setup.")
    nserver.setup()
    poly.LOGGER.info("Setup completed. Running Server.")
    nserver.run()
    
if __name__ == "__main__":
    main()
