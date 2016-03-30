from polyglot.nodeserver_api import Node
import soco

class SonosControl(Node):
    
    def __init__(self, *args, **kwargs):
        super(SonosControl, self).__init__(*args, **kwargs)
    
    def _discover(self, **kwargs):
        manifest = self.parent.config.get('manifest', {})
        self.parent.poly.LOGGER.info("Received Discover command from ISY.")
        speakers = soco.discover()
        for speaker in speakers:
            # ISY only allows 14 character limit on nodes, have to strip the RINCON and use the first 14 chars of the UID
            address = speaker.uid[8:22].lower()
            lnode = self.parent.get_node(address)
            if not lnode:
                self.parent.poly.LOGGER.info("New Speaker Found.")
                self.parent.speakers.append(SonosSpeaker(self.parent, self.parent.get_node('sonoscontrol'), address, speaker.player_name,  speaker.ip_address, manifest))
        self.parent.update_config()
        return True        

    _drivers = {}

    _commands = {'DISCOVER': _discover}
    
    node_def_id = 'sonoscontrol'

class SonosSpeaker(Node):
    
    def __init__(self, parent, primary, address, player_name, ip_address, manifest=None):
        self.parent = parent
        self.LOGGER = self.parent.poly.LOGGER
        self.ip = ip_address
        self.zone = soco.SoCo(self.ip)
        self.player_name = player_name
        self.address = address
        self.LOGGER.info("Adding new Sonos Speaker: " + self.player_name + "@" + self.ip + " Current Volume: " + str(self.zone.volume))
        super(SonosSpeaker, self).__init__(parent, address, "Sonos " + player_name, primary, manifest)
        self.LOGGER.info("Getting current speaker volume, bass and treble...")
        self.update_info()
        
    def _update_node(self):
        self.parent.poly.LOGGER.info("Updating ISY information with IP address and current volume.")
        ip_addr = self.ip.split('.')
        for ind, driver in enumerate(('GV1', 'GV2', 'GV3', 'GV4')):
                self.set_driver(driver, ip_addr[ind])
        self.update_info()

    def update_info(self):
        self.set_driver('ST', self.zone.volume)
        self.set_driver('GV1', self.zone.bass)
        self.set_driver('GV2', self.zone.treble)

    def _play(self, **kwargs):
        self.zone.play()
        return True
        
    def _stop(self, **kwargs):
        self.zone.stop()
        return True

    def _pause(self, **kwargs):
        self.zone.pause()
        return True        

    def _next(self, **kwargs):
        self.zone.next()
        return True

    def _previous(self, **kwargs):
        try:
            self.zone.previous()
        except:
            self.LOGGER.info("Error in command 'previous'. This typically means that the station or mode you are in doesn't support it.")
        return True        

    def _partymode(self, **kwargs):
        self.zone.partymode()
        return True

    def _mute(self, **kwargs):
        if self.zone.mute:
            self.zone.mute = False
        else: 
            self.zone.mute = True
        return True
        
    def _volume(self, **kwargs):
        val = kwargs.get('value')
        if val:
            self.zone.volume = int(val)
            self.set_driver('ST', int(val), 56)
        return True

    def _bass(self, **kwargs):
        val = kwargs.get('value')
        if val > -11 or val < 11:
            self.zone.bass = val
            self.set_driver('GV1', int(val), 56)
        return True

    def _treble(self, **kwargs):
        val = kwargs.get('value')
        if val > -11 or val < 11:
            self.zone.treble = val
            self.set_driver('GV2', int(val), 56)
        return True

    def query(self, **kwargs):
        self.update_info()
        return True

    _drivers = {'GV1': [0, 56, int], 'GV2': [0, 56, int],
                'GV3': [0, 56, int], 'GV4': [0, 56, int],
                'ST': [0, 51, int]}

    _commands = {'PLAY': _play,       
                            'STOP': _stop,
                            'DON': _play,
                            'DOF': _pause,
                            'PAUSE': _pause,
                            'NEXT': _next,
                            'PREVIOUS': _previous,
                            'PARTYMODE': _partymode,
                            'MUTE': _mute,
                            'BASS': _bass,
                            'TREBLE': _treble,
                            'VOLUME': _volume}
                            
    node_def_id = 'sonosspeaker'