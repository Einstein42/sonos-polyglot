import json
from polyglot.nodeserver_api import Node

class SonosControl(Node):
    
    def __init__(self, *args, **kwargs):
        super(SonosControl, self).__init__(*args, **kwargs)
    
    def _discover(self, **kwargs):
        return self.parent.discover()

    _drivers = {}

    _commands = {'DISCOVER': _discover}
    
    node_def_id = 'sonoscontrol'

class SonosSpeaker(Node):
    
    def __init__(self, *args, **kwargs):
        super(SonosSpeaker, self).__init__(*args, **kwargs)

    def _play(self):
        return True
    
    def _stop(self):
        return True

    _drivers = {}

    _commands = {'PLAY': _play,
                            'STOP': _stop}
                            
    node_def_id = 'sonosspeaker'