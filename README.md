# sonos-polyglot

#Requirements
sudo pip install soco

Install:

1. Go to your polyglot/config/node_servers/ folder
2. git clone git@github.com:Einstein42/sonos-polyglot.git
3. Restart Polyglot and add Sonos nodeserver via web interface
4. Download profile and copy baseURL from polyglot
5. Add as NodeServer in ISY. Upload profile.
6. Reboot ISY
7. Upload Profile again in the node server (quirk of ISY)
8. Reboot ISY again (quirk of ISY)
9. Once ISY is back up, go to Polyglot and restart the Sonos nodeserver.
10. All speakers will be automatically added as 'Sonos <whatever you have it named>'
11. Write programs and enjoy.


I build this on ISY version 5.0.2 and the current polyglot DEV version from 
https://github.com/UniversalDevicesInc/Polyglot


