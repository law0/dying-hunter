# coding: utf-8

import random
from game.bot import *

class PlayerManager:

    def __init__(self):
        self.bots = {}
        self.players = {}
        self.arena = None

    def dump(self):
        self.bots = {}
        self.players = {}
        self.arena = None

    def setArena(self, arena):
        self.arena = arena
        for who in self.players.keys():
            self.connectPlayer(who, True)

    def getArenaView(self):
        if self.arena == None:
            return None
        res = {}
        ser = self.arena.serialize()
        res["gameId"] = ser["gameId"]
        res["remainingTicks"] = ser["remainingTicks"]
        res["state"] = ser["state"]
        res["board"] = ser["board"]
        return res

    def addBot(self, name):
        if self.arena == None:
            return
        self.bots[name] = self.arena.addPlayer(name)

    def connectPlayer(self, name, newArena):
        if self.arena == None:
            return False
        if not name in self.players.keys() or newArena:
            self.players[name] = [self.arena.addPlayer(name), None] # 0: player 1: direction
        return True

    def addMoveRequest(self, name, direction):
        if self.arena == None:
            return False
        player = self.players[name][0]
        self.players[name] = [player, direction]
        return True

    def getPlayerView(self, name):
        if self.arena == None:
            return None
        return self.getArenaView()


    def performTick(self):
        self.moveBots()
        self.movePlayers()

    def moveBots(self):
        if self.arena == None:
            return
        if len(self.bots) == 0:
            return
        directions = ["UP", "LEFT", "DOWN", "RIGHT"]
        bots = list(self.bots.keys())
        random.shuffle(bots)
        for bot in bots:
            if self.bots[bot].alive:
                if bot[:5] == "smart":
                    self.arena.move(bot, get_clever_move(bot, self.arena.board))
                else:
                    self.arena.move(bot, random.choice(directions))

    def movePlayers(self):
        if self.arena == None:
            return
        if len(self.players) == 0:
            return
        players = list(self.players.keys())
        random.shuffle(players)
        for who in players:
            data = self.players[who]
            player = data[0]
            direction = data[1]
            if player != None and player.alive and direction != None:
                self.arena.move(who, direction)
                self.players[who] = [player, None]
