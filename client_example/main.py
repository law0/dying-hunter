#!/usr/bin/env python3
# coding: utf-8

import argparse
import json
import math
import socket
import sys
import time

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
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('localhost', 8082)
    sock.connect(server_address)
    print("Sending hello")
    cmd = "HELLO:"+myName
    cmd = cmd.rjust(12," ")
    sock.sendall(cmd.encode("utf-8"))
    res = sock.recv(2).decode("utf-8")
    if res != "OK":
        print("Hello was refused")
        return 1
    xTurn = True
    while True:
        cmd = "VIEW"
        cmd = cmd.rjust(12," ")
        sock.sendall(cmd.encode("utf-8"))
        res = sock.recv(2).decode("utf-8")
        if res != "LG":
            continue
        jsonLen = int(sock.recv(4).decode("utf-8"))
        jsonData = sock.recv(jsonLen).decode("utf-8")
        #Retrive last OK
        res = sock.recv(2).decode("utf-8")
        view = json.loads(jsonData)
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
        #Readind the board
        for x in range(0,len(board)):
            for y in range(0,len(board[0])):
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
        cmd = "MOVE:"+direction
        cmd = cmd.rjust(12," ")
        sock.sendall(cmd.encode("utf-8"))
        xTurn = not xTurn
        time.sleep(1)

if __name__ == "__main__":
    sys.exit(main())
