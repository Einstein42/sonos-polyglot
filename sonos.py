#!/usr/bin/python
""" Sonos Node Server for Polyglot """

import requests
from polyglot.nodeserver_api import SimpleNodeServer, PolyglotConnector, auto_request_report, Node
from sonos_types import SonosSpeaker, SonosControl
import soco

VERSION = "0.0.1"


class SonosNodeServer(SimpleNodeServer):
    """ Sonos Node Server """
    controller = None

    def setup(self):
        manifest = self.config.get('manifest',{})
        SonosControl(self,'sonoscontrol','Sonos Control', True, manifest)
        self.update_config()
        self.poly.LOGGER.info("FROM Poly ISYVER: " + self.poly.isyver)
        self.long_poll()

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

    def discover(self):
        manifest = self.config.get('manifest', {})
        self.poly.LOGGER.info("Received Discover command from ISY")
        speakers = soco.discover()
        for speaker in speakers:
            address = speaker.uid[8:20].lower()
            lnode = self.get_node(address)
            if not lnode:
                SonosSpeaker(self, address, 'Sonos ' + speaker.player_name, self.get_node('sonoscontrol'), manifest)
        self.update_config()
        return True
        
def main():
    """ setup connection, node server, and nodes """
    poly = PolyglotConnector()
    nserver = SonosNodeServer(poly)
    poly.connect()
    poly.wait_for_config()
    poly.LOGGER.info("Sonos Interface version " + VERSION + " created. Initiating setup.")
    nserver.setup()
    poly.LOGGER.info("Setup completed. Running Server.")
    nserver.run()
    
if __name__ == "__main__":
    main()
