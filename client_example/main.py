#!/usr/bin/env python3
# coding: utf-8

import argparse
import json
import math
import socket
import sys
import time
import random

SERVER_ADDR='localhost'
SERVER_PORT=8082
DEMO_MODE="random"

"""
README !
This a simple example of an avatar controller for the dying hunter game.
It is advise to first look at the main() directly.

This example implements two strategies:
    1. "random", you guessed it, it does random moves
    2. "simple", goes to closest player if hunter, run away from hunter otherwise

A simple api (dhapi_*) is provided, but you're free to implement your own
as it is quite simple (really. It just open a socket and send stuff)

"""




"""
################
The 'API'
################
"""
def dhapi_get_socket(server_addr=SERVER_ADDR, server_port=SERVER_PORT):
    if not hasattr(dhapi_get_socket, "sock"):
        dhapi_get_socket.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (server_addr, server_port)
        dhapi_get_socket.sock.connect(server_address)
    return dhapi_get_socket.sock

# Subscribe ourselves to the game server
def dhapi_send_hello(team_name):
    print("Sending hello {}".format(team_name))
    cmd = "HELLO:"+team_name

    #server needs strings of 12 chars Exactly
    cmd = cmd.rjust(12," ")

    sock = dhapi_get_socket()

    sock.sendall(cmd.encode("utf-8"))
    res = sock.recv(2).decode("utf-8")
    if res != "OK":
        print("Hello was refused")
        return False
    return True

# Move UP
def dhapi_send_UP():
    dhapi_get_socket().sendall("MOVE:UP".rjust(12, " ").encode("utf-8"))

# Move DOWN
def dhapi_send_DOWN():
    dhapi_get_socket().sendall("MOVE:DOWN".rjust(12, " ").encode("utf-8"))

# Move LEFT
def dhapi_send_LEFT():
    dhapi_get_socket().sendall("MOVE:LEFT".rjust(12, " ").encode("utf-8"))

# Move RIGHT
def dhapi_send_RIGHT():
    dhapi_get_socket().sendall("MOVE:RIGHT".rjust(12, " ").encode("utf-8"))

# Ask the game server for a view of current game status
def dhapi_get_view():
    cmd = "VIEW"
    cmd = cmd.rjust(12," ")

    sock = dhapi_get_socket()

    sock.sendall(cmd.encode("utf-8"))
    res = sock.recv(2).decode("utf-8")

    #After a VIEW cmd, server returns "LG"
    if res != "LG":
        return None

    jsonLen = int(sock.recv(4).decode("utf-8"))
    jsonData = sock.recv(jsonLen).decode("utf-8")
    #Retrieve last OK

    res = sock.recv(2).decode("utf-8")
    view = json.loads(jsonData)

    return view






"""
################
The example
################
"""
# A class representing players. Note that you don't have to use it at all.
# You can do your own, or do otherwise.
class Player:
    def __init__(self, x, y, name, role):
        self.x = x
        self.y = y
        self.name = name
        self.role = role



# Guess what it does
def random_play():
    return random.choice(["UP", "DOWN", "LEFT", "RIGHT"])

# Go to the closest if hunter, else run away from hunter
def simple_play(view, team_name):
    me = Player(0, 0, team_name, " ")
    hunter = Player(0, 0, " ", "H")
    players = []
    imHunter = False
    board = view["board"]

    #Reading the board
    for x in range(0, len(board)):
        for y in range(0, len(board[0])):
            if len(board[x][y]) != 0:
                split = board[x][y].split("/")
                name = split[0]
                role = split[1]
                status  = split[2]
                if name == team_name:
                    #print(board[x][y])
                    me.x = x
                    me.y = y
                    imHunter = (role == "H")
                elif role == "H":
                    hunter.x = x
                    hunter.y = y
                    hunter.name = name
                else:
                    players.append(Player(x, y, name, role))

    direction = ""
    moves = [("UP", me.x, me.y-1),
             ("DOWN", me.x, me.y+1),
             ("LEFT", me.x-1, me.y),
             ("RIGHT", me.x+1, me.y)]

    #distance = lambda x0,y0,x1,y1: math.sqrt((x0 - x1)**2 + (y0 - y1)**2)
    distance = lambda x0,y0,x1,y1: abs(x0 - x1) + abs(y0 - y1)

    #Choose what to do
    if imHunter:
        print("I'm hunter!")
        #Chase closest player

        # Get closest player
        target = sorted(players, key=lambda p: distance(p.x,p.y,me.x,me.y))[0]

        print("Closest player {} at x:{} y:{}".format(target.name, target.x, target.y))
        print("Me x:{} y:{}".format(me.x, me.y))

        # choose the move that will minimize the distance
        direction = sorted(moves, key=lambda move: distance(target.x,target.y,move[1],move[2]))[0][0]

    else:
        print("I'm player!")
        #Run AWAY from hunter
        print("Hunter {} at x:{} y:{}".format(hunter.name, hunter.x, hunter.y))
        print("Me x:{} y:{}".format(me.x, me.y))

        # choose the move that will maximize the distance
        direction = sorted(moves, key=lambda move: distance(hunter.x,hunter.y,move[1],move[2]), reverse=True)[0][0]

    print("I'm going {}\n\n".format(direction))

    return direction





"""
###############
The main stuff
###############
"""
def init_arguments():
    parser = argparse.ArgumentParser(description='dying wolf client example')
    parser.add_argument('-n', '--name', dest='name',
                          help='Name of the client', default="Dumb")
    parser.add_argument('--addr', dest='server_addr',
                          help='server addr, default: localhost', default='localhost')
    parser.add_argument('--port', dest='server_port',
                          help='server port, default: 8082', default=8082)
    parser.add_argument('--demo-mode', dest='demo_mode',
                          help='Mode for this demo avatar: random or simple, default: random', 
                          default='random')
    return parser.parse_args()



def main():
    arg_parsed = init_arguments()
    team_name = arg_parsed.name
    SERVER_ADDR = arg_parsed.server_addr
    SERVER_PORT = arg_parsed.server_port
    DEMO_MODE = arg_parsed.demo_mode
    

    # Connect us to a game !
    if not dhapi_send_hello(team_name):
        print("Couldn't say hello")
        return 1

    while True:
        # Get a view of the current state of the grid
        view = dhapi_get_view()
        if view is None:
            continue

        state = view["state"]
        if state != 2:
            #Game is pending, ready or ended so nothing to do
            continue

        #Game is running !

        # Choose a direction in function of the game status !
        # This is probably where you will code your strategies !
        direction = random_play() if DEMO_MODE == "random" else simple_play(view, team_name)

        if direction == "UP":
            dhapi_send_UP()
        elif direction == "DOWN":
            dhapi_send_DOWN()
        elif direction == "LEFT":
            dhapi_send_LEFT()
        elif direction == "RIGHT":
            dhapi_send_RIGHT()

        time.sleep(1)

if __name__ == "__main__":
    sys.exit(main())
