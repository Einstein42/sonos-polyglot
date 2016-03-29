#!/usr/bin/python
""" MyQ Node Server for Polyglot """

import requests
from polyglot.nodeserver_api import SimpleNodeServer, PolyglotConnector, auto_request_report, Node

USERNAME = 'milne.alarm.system@gmail.com'
PASSWORD = 'smilne11'
SERVICE = 'https://myqexternal.myqdevice.com'

APPID = 'Vj8pQggXLhLy0WHahglCD4N1nAkkXQtGYpq2HrHD7H1nvmbT55KqtN6RSF4ILB%2fi'
CULTURE = 'en'

STATES = ['',
        'Open',
        'Closed',
        'Stopped',
        'Opening',
        'Closing',
        ]

# Class to instantiate the door objects
class DOOR:
    instances = []

    def __init__(self, id, name, state):
        DOOR.instances.append(self)
        self.id = id
        self.name = name
        self.state = state

    def get_id(self):
        return self.id

class MyQ(object):

    def __init__(self):
        pass

    def get_token(self):
        try:
            # Create connection URL to get auth token
            login_url = SERVICE + '/Membership/ValidateUserWithCulture?appId=' + APPID + '&securityToken=null&username=' + USERNAME + '&password=' + PASSWORD + '&culture=' + CULTURE
            # Get json data from Chamberlain and extract token
            r = requests.get(login_url)
            data = r.json()
            # If json response ReturnCode == 0, it was succesful
            if data['ReturnCode'] != '0':
                self.LOGGER.info('Get Token Error: ' + data['ErrorMessage'])
                return
            # Return the token
            return data['SecurityToken']
        #Catch and log any errors by the request
        except requests.exceptions.RequestException as err:
           self.LOGGER.info('Get Token Connection Error: ' + e)
           return


    def get_doors(self,token):
        try:
            # Create connection URL for door data collection
            system_detail = SERVICE + '/api/UserDeviceDetails?appId=' + APPID + '&securityToken=' + token
            # Get json data from Chamberlain listing doors
            r = requests.get(system_detail)
            data = r.json()
            # If json response ReturnCode == 0, it was succesful
            if data['ReturnCode'] != '0':
               self.LOGGER.info("Get Doors Error %s", data['ErrorMessage'])
               return False
            # Check each instance of Devices in returned json and pull out just the doors
            for device in data['Devices']:
            #MyQDeviceTypeId Doors == 2, Gateway == 1, Structure == 10, Thermostat == 11
                if device['MyQDeviceTypeId'] == 2:
                    # Assume this is a new door
                    existing = False
                    # Get device ID from json response
                    id = device['DeviceId']
                    # Check existing instances and update state if found.
                    for inst in DOOR.instances:
                        if inst.id == id:
                            existing = True
                            inst.state = self.get_doorstate(token, device['DeviceId'])
                    # If not found in existing, create new door instance.
                    if not existing:
                       name = self.get_doorname(token, device['DeviceId'])
                       self.LOGGER.info('Adding Door to ISY - Name: %s ID: %s', name, id)
                       DOOR(id, name,self.get_doorstate(token, device['DeviceId']))
            return True
        #Catch and log any errors by the request               
        except requests.exceptions.RequestException as err:
           self.LOGGER.info('Get Doors Connection Error: ' + e)
           return False


    def get_doorstate(self,token, id):
        try:
            # Create connection URL for door data collection        
            doorstate_url = SERVICE + '/Device/getDeviceAttribute?appId=' + APPID + '&securityToken=' + token + '&devId=' + id + '&name=doorstate' 
            # Get json data from Chamberlain listing door state for id
            r = requests.get(doorstate_url)
            data = r.json()
            # If json response ReturnCode == 0, it was succesful
            if data['ReturnCode'] != '0':
               self.LOGGER.info('Get Doorstate Error: ' + data['ErrorMessage'])
               return
            return STATES[int(data['AttributeValue'])]
        #Catch and log any errors by the request               
        except requests.exceptions.RequestException as err:
           self.LOGGER.info('Get Doorstate Connection Error: ' + err)
           return

    def get_doorname(self,token, id):
        try:
            # Create connection URL for door data collection        
            doorstate_url = SERVICE + '/Device/getDeviceAttribute?appId=' + APPID + '&securityToken=' + token + '&devId=' + id + '&name=desc'
            # Get json data from Chamberlain listing door name for id            
            r = requests.get(doorstate_url)
            data = r.json()
            # If json response ReturnCode == 0, it was succesful
            if data['ReturnCode'] != '0':
               self.LOGGER.info('Get Doorname Error: ' + data['ErrorMessage'])
            return data['AttributeValue']
        #Catch and log any errors by the request                           
        except requests.exceptions.RequestException as err:
           self.LOGGER.info('Get Doorstate Connection Error: ' + err)
           return

    def myq_connect(self):
        # Connect to Chamberlain and get door information
        token = self.get_token()
        self.LOGGER.info("MyQ Connect: %s", token)
        return True

class MQSimpleNodeServer(SimpleNodeServer):

    #hub = None
    def setup(self):
        manifest = self.config.get('manifest',{})
        #self.nodes['mqhub'] = MQHUB(self, 'mqhub', 'MyQ Server Node', manifest)
        """"
        self.add_node(MQHUB(self, 'mqhub', 'MyQ Server Node', True, manifest))
        """
        self.update_config()
        self.poly.LOGGER.info("FROM Poly ISYVER: " + self.poly.isyver)
        self.long_poll()

    def long_poll(self):
        """
        manifest = self.config.get('manifest', {})
        self.controls = MyQ()
        token = self.controls.get_token()
        if token:
            self.controls.get_doors(token)
        else:
            self.LOGGER.info('Long Poll, no token present.')
        for inst in DOOR.instances:
            if inst.id not in self.nodes:
                self.nodes[inst.id] = MQDOOR(self, inst.id, inst.name, manifest)
                self.update_config()
            if inst.state == "Open":
                self.nodes[inst.id].set_driver('ST', 100)
                #LOGGER.info('OPEN DOOR: Set %s door to %s', inst.name, inst.state)
            else:
                self.nodes[inst.id].set_driver('ST', 0)
                #LOGGER.info('CLOSED DOOR: Set %s door to %s', inst.name, inst.state)
        """
        return True


class MQDOOR(Node):
    # Node representing MyQ Door 
    def __init__(self, parent, address, name, manifest=None):
        super(MQDOOR, self).__init__(parent, id, name, manifest)
        manifest = manifest.get(address, {}) if manifest else {}
        new_node = manifest == {}
        self.parent = parent
        self.address = address
        self.added = manifest.get('added', False)
        self.name = manifest.get('name', name)
        
        drivers = manifest.get('drivers', {})
        for key, value in self._drivers.items():
            self._drivers[key][0] = drivers.get(key, value[0])

        if new_node:
            all_nodes = list(self.parent.nodes.keys())
            #LOGGER.info('%s', all_nodes)
            if len(all_nodes) > 0:
                primary = all_nodes[0]
            else:
                primary = address
            self.add_node(primary)
            self.added = manifest.get('added', True)

    def run_cmd(self, command, **kwargs):
            """
            Runs one of the node's commands.

            :param str command: The name of the command
            :param dict kwargs: The parameters specified by the ISY in the
                                incoming request. See the ISY Node Server
                                documentation for more information.
            :returns boolean: Indicates success or failure of command
            """
            self.LOGGER.info('Command: ' + command)
            return True
            if command in self._commands:
                fun = self._commands[command]
                success = fun(self, **kwargs)
                
            return False            

    def _changestate(self, id, status):
        pass
        
    _drivers = {'ST': [0, 97, int]}
    _commands = {'OPEN': _changestate, 
                            'CLOSE': _changestate}
    node_def_id = 'MQDOOR'
 
 
class MQHUB(Node):
    """ Node representing MyQ HUB """

    def __init__(self, parent, address, name, prim, manifest=None):
        super(MQHUB, self).__init__(parent, address, name, prim, manifest)
        manifest_address = manifest.get(address, {}) if manifest else {}
        manifest_name = manifest.get(name, {}) if manifest else {}
        self.LOGGER.info('man: %s\n man2: %s', manifest_address, manifest_name)
        new_node = manifest == {}
        self.parent = parent
        self.address = address
        #self.state = state
        self.added = manifest.get('added', False)
        #self.name = manifest.get('name', name)
        self.name = name
        self.LOGGER.info("Adding MyQ Hub - Address: %s Name: %s New_Node: %s", address, name, new_node)
        
        drivers = manifest.get('drivers', {})
        for key, value in self._drivers.items():
            self._drivers[key][0] = drivers.get(key, value[0])

        if new_node:
            all_nodes = list(self.parent.nodes.keys())
            if len(all_nodes) > 0:
                primary = all_nodes[0]
            else:
                primary = address
            self.LOGGER.info('!!!!!!!!! %s', str(primary))    
            self.add_node(primary)
            self.added = manifest.get('added', True)
            

    def run_cmd(self, command, **kwargs):
            """
            Runs one of the node's commands.

            :param str command: The name of the command
            :param dict kwargs: The parameters specified by the ISY in the
                                incoming request. See the ISY Node Server
                                documentation for more information.
            :returns boolean: Indicates success or failure of command
            """
            if command in self._commands:
                fun = self._commands[command]
                success = fun(self, **kwargs)
                return success
            return False            
    def _connect(self):
        pass

            
    def _changestate(self, id, status):
        pass
        
    _drivers = {'ST': [0, 2, int]}
    _commands = {'CONNECT': _connect}
    node_def_id = 'MQHUB'



def main():
    """ setup connection, node server, and nodes """
    poly = PolyglotConnector()
    nserver = MQSimpleNodeServer(poly)
    poly.connect()
    poly.wait_for_config()
    nserver.setup()
    nserver.run()
    


if __name__ == "__main__":
    main()
