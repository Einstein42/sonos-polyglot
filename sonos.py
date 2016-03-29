#!/usr/bin/python
""" Sonos Node Server for Polyglot """

import requests
from polyglot.nodeserver_api import SimpleNodeServer, PolyglotConnector, auto_request_report, Node

VERSION = "0.0.1"


class SonosNodeServer(SimpleNodeServer):

    def setup(self):
        manifest = self.config.get('manifest',{})
        self.update_config()
        self.poly.LOGGER.info("FROM Poly ISYVER: " + self.poly.isyver)
        self.long_poll()

    def long_poll(self):
        return True

def main():
    """ setup connection, node server, and nodes """
    poly = PolyglotConnector()
    nserver = SonosNodeServer(poly)
    poly.connect()
    poly.wait_for_config()
    poly.LOGGER("Sonos Interface version " + VERSION + "created. Initiating setup.")
    nserver.setup()
    nserver.run()
    
if __name__ == "__main__":
    main()
