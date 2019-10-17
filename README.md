# UtouchGPSServer
  This is a simple python 3 server that uses gps_test to pull elevation, longitude and latitude in  such a way as to be useful as an alternative location source for Activity Tracker.  The server is base
d on this code: https://framagit.org/ernesst/gps-utouch-tracker/blob/master/GPS_tracking.py 

## What does it do?
It sits around listening on the socket_address and socket_port for someone to say the socket_secret.  When it gets the socket_secret it runs "test_gps" for "retry_limit" frames.  If it gets a valid location before hitting the limit, it returns the elevation, latitude and longitude to the client.  Otherwise it'll return "invalid" if the location could not be determined.  If the secret was invalid it will return "bad secret".

## How do you work this thing?
In the server you can modify:
  
* socket_address
* socket_port
* socket_secret

The script must be run as root, so probably best to make it executable and use sudo to run it like so:
  
  __chmod +x track_attack_server.py__
  
  __sudo ./track_attack_server.py__

This should start the server listening.  

## How do I connect to it
you can use track_attack_client.py as an example on how to connect and use this server.
