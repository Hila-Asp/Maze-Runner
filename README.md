# Maze Runner

An online game multiplayer game of catch. Supports 2-7 players playing against opponents online.</br>
There is a feature of an apple that if a player "eats" it, the player can pass through walls for 5 seconds. </br>
Every 10 seconds the apple changes location. </br>
All the data transfered over the network is encrypted with SSL and all the saved password are hashed with salt and pepper. </br>
This project was created using python 3.8, pygame and the sockets module from python3.

# To make this code work

- you need to change the addresses in the project if you did not save the project in the same folder as I did.
- You need to create your own SSL certificates and CA and change their address in client.py and server.py and the server IP (according to the domain name of the server certificate) in client.py.
- You need to add the domain name of the server certificate as the server's IP address in your computer's "hosts" file.
- You need to first run server_init.py to reset the server's password.
- You need to download the modules that appear in requirements.txt
