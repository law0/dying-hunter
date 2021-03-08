#!/usr/bin/env python3
# coding: utf-8

import argparse
import json
import math
import socket
import sys
import time

def dhapi_get_socket(server_addr='localhost', server_port=8082):
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




class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y

def init_arguments():
    parser = argparse.ArgumentParser(description='dying wolf client example')
    parser.add_argument('-n', '--name', dest='name',
                          help='Name of the client', default="Dumb")
    return parser.parse_args()



def main():
    arg_parsed = init_arguments()
    myName = arg_parsed.name
    
    if not dhapi_send_hello(myName):
        print("Couldn't say hello")
        return 1

    xTurn = True
    while True:
        view = dhapi_get_view()
        if view is None:
            continue

        state = view["state"]
        if state != 2:
            #Game is pending, ready or ended so nothing to do
            continue
        #Game is running !
        me = Player(0, 0)
        hunter = Player(0, 0)
        players = []
        imHunter = False
        board = view["board"]

        #Reading the board
        for x in range(len(board)):
            for y in range(len(board[0])):
                if len(board[x][y]) != 0:
                    split = board[x][y].split("/")
                    name = split[0]
                    role = split[1]
                    status  = split[2]
                    if name == myName:
                        print(board[x][y])
                        me.x = x
                        me.y = y
                        imHunter = (role == "H")
                        print(imHunter)
                    elif role == "H":
                        hunter.x = x
                        hunter.y = y
                    else:
                        players.append(Player(x, y))

        #Choose what to do
        direction = ""
        if imHunter:
            #Chase closest player
            target = None
            dist = -1
            print(players)
            for player in players:
                player_dist = math.sqrt((player.x-me.x)**2+(player.y-me.y)**2)
                if dist < 0 or player_dist < dist:
                    dist = player_dist
                    target = player

            print("Target x:{} y:{}".format(target.x, target.y))
            print("Me x:{} y:{}".format(me.x, me.y))
            if xTurn:
                direction = "LEFT"
                if(target.x > me.x):
                    direction = "RIGHT"
            else:
                direction = "UP"
                if(target.y > me.y):
                    direction = "DOWN"
        else:
            #Run away from hunter
            print("Hunter x:{} y:{}".format(hunter.x, hunter.y))
            print("Me x:{} y:{}".format(me.x, me.y))
            if xTurn:
                direction = "RIGHT"
                if(hunter.x >= me.x):
                    direction = "LEFT"
            else:
                direction = "DOWN"
                if(hunter.y >= me.y):
                    direction = "UP"



        print(direction)
        if direction == "UP":
            dhapi_send_UP()
        elif direction == "DOWN":
            dhapi_send_DOWN()
        elif direction == "LEFT":
            dhapi_send_LEFT()
        elif direction == "RIGHT":
            dhapi_send_RIGHT()


        xTurn = not xTurn
        time.sleep(1)

if __name__ == "__main__":
    sys.exit(main())
