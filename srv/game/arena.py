# coding: utf-8

import random
from enum import IntEnum

from game.player import *


class State(IntEnum):
    PENDING = 0
    READY = 1
    RUNNING = 2
    ENDED = 3
    TOURNAMENTSUB = 4

class Mode(IntEnum):
    NORMAL = 0
    PLAYGROUD = 1

class ArenaConstants:
    c_runDuration = 60
    c_pauseDuration = 5

class Arena:

    def __init__(self, id, length, height):
        self.id = id
        self.state = State.PENDING
        self.stateReminingTick = 0
        self.board = None
        self.length = length
        self.height = height
        self.players = {}
        self.mode = Mode.NORMAL
        self.initBoard()

    def initBoard(self):
        self.board = [[ None for x in range(0,self.length)] for y in range(0,self.height)]

    def setPlayground(self):
        self.mode = Mode.PLAYGROUD

    def dump(self):
        self.state = State.ENDED
        self.stateReminingTick = 0
        self.players = {}
        self.mode = Mode.NORMAL
        self.initBoard()

    def addPlayer(self, name):
        if self.state != State.PENDING and self.state != State.TOURNAMENTSUB:
            return None
        player = Player(name)
        placed = False
        while not placed:
            player.x = random.randint(0,self.length-1)
            player.y = random.randint(0,self.height-1)
            placed = self.board[player.x][player.y] == None
        self.players[name] = player
        self.board[player.x][player.y] = player
        return player

    def getPlayer(self, name):
        if name in self.players.keys():
            return self.players[name]
        return None

    def chooseHunter(self):
        found = False
        while not found:
            hunter = random.choice(list(self.players.values()))
            found = hunter.alive
        hunter.role = Role.HUNTER
        hunter.status = Status.NORMAL
        for player in self.players.values():
            if player != hunter:
                player.role = Role.PREY
                player.status = Status.NORMAL

    def performTick(self):
        if self.state == State.ENDED or self.state == State.PENDING:
            return
        self.stateReminingTick -= 1

        if self.state == State.READY:
            if self.stateReminingTick <= 0:
                self.state = State.RUNNING
                self.stateReminingTick = ArenaConstants.c_runDuration
            return

        if self.state == State.RUNNING:
            for player in self.players.values():
                if player.status == Status.FROZEN:
                    if player.statusTime > 3:
                        player.status = Status.NORMAL
                        player.statusTime = 0
                    else:
                        player.statusTime += 1
                if player.status == Status.SAFE:
                    if player.statusTime > 3:
                        player.status = Status.NORMAL
                        player.statusTime = 0
                    else:
                        player.statusTime += 1
            if self.stateReminingTick <= 0:
                if self.mode == Mode.NORMAL:
                    aliveCount = sum(map(lambda x : x.alive, self.players.values()))
                    if aliveCount > 2:
                        toRemove = None
                        self.killHunter()
                        self.chooseHunter()
                        self.state = State.READY
                        self.stateReminingTick = ArenaConstants.c_pauseDuration
                    else:
                        self.endGame()
                else:
                    self.stateReminingTick = ArenaConstants.c_runDuration

    def killHunter(self):
        hunter = None
        aliveCount = sum(map(lambda x : x.alive, self.players.values()))
        for player in self.players.values():
            if player.role == Role.HUNTER:
                hunter = player
                player.alive = False
                player.position = aliveCount
                break
        self.board[hunter.x][hunter.y] = None


    def endGame(self):
        self.state = State.ENDED
        for player in self.players.values():
            if player.alive:
                if player.role == Role.HUNTER:
                    player.position = 2
                else:
                    player.position = 1
                player.alive = False

    def startGame(self):
        self.state = State.READY
        self.chooseHunter()
        self.stateReminingTick = ArenaConstants.c_pauseDuration

    def move(self, name, direction):
        player = self.players[name]
        newX = player.x
        newY = player.y
        if self.state != State.RUNNING:
            return
        if player.status == Status.FROZEN or not player.alive:
            return
        if direction == "UP":
            if player.y > 0:
                newY -= 1
        elif direction == "DOWN":
            if player.y < self.height-1:
                newY += 1
        elif direction == "RIGHT":
            if player.x < self.length-1:
                newX += 1
        elif direction == "LEFT":
            if player.x > 0:
                newX -= 1
        #Todo handle colision and status
        if newX == player.x and newY == player.y:
            return
        if self.board[newX][newY] == None:
            self.board[player.x][player.y] = None
            player.x = newX
            player.y = newY
            self.board[player.x][player.y] = player
        else:
            contact = self.board[newX][newY]
            if player.role == Role.HUNTER and contact.role == Role.PREY:
                if contact.status != Status.SAFE:
                    contact.role = Role.HUNTER
                    contact.status = Status.NORMAL
                    player.role = Role.PREY
                    player.status = Status.SAFE
                    player.statusTime = 0
            elif contact.role == Role.HUNTER and player.role == Role.PREY:
                player.role = Role.HUNTER
                player.status = Status.NORMAL
                contact.role = Role.PREY
                contact.status = Status.SAFE
                contact.statusTime = 0
            elif contact.role == Role.PREY:
                if contact.status != Status.SAFE and contact.status != Status.FROZEN:
                    contact.status = Status.FROZEN
                    contact.statusTime = 0

    def setPosition(self, name, x, y):
        player = self.players[name]
        if self.board[x][y] == None:
            self.board[player.x][player.y] = None
            player.x = x
            player.y = y
            self.board[player.x][player.y] = player
        else:
            contact = self.board[x][y]
            if player.role == Role.HUNTER and contact.role == Role.PREY:
                if contact.status != Status.SAFE:
                    contact.role = Role.HUNTER
                    contact.status = Status.NORMAL
                    player.role = Role.PREY
                    player.status = Status.SAFE
                    player.statusTime = 0
            elif contact.role == Role.HUNTER and player.role == Role.PREY:
                player.role = Role.HUNTER
                player.status = Status.NORMAL
                contact.role = Role.PREY
                contact.status = Status.SAFE
                contact.statusTime = 0
            elif contact.role == Role.PREY:
                if contact.status != Status.SAFE and contact.status != Status.FROZEN:
                    contact.status = Status.FROZEN
                    contact.statusTime = 0

    def setHunter(self, name):
        for player in self.players.values():
            if player.role == Role.HUNTER:
                player.role = Role.PREY
                player.status = Status.NORMAL
        player = self.players[name]
        player.role = Role.HUNTER
        player.status = Status.NORMAL

    def setFrozen(self, name):
        player = self.players[name]
        if player.role != Role.HUNTER:
            player.status = Status.FROZEN

    def setSafe(self, name):
        player = self.players[name]
        if player.role != Role.HUNTER:
            player.status = Status.SAFE

    def setNormal(self, name):
        player = self.players[name]
        if player.role != Role.HUNTER:
            player.status = Status.NORMAL

    def getWinner(self):
        if self.state != State.ENDED:
            return None
        for player in self.players.values():
            if player.position == 1:
                return player.name
        return None

    def getRanking(self):
        if self.state != State.ENDED:
            return None
        ratable = {}
        for player in self.players.values():
                ratable[player.position] = player.name
        ranking = []
        for pos in sorted(ratable.keys()):
            ranking.append(ratable[pos])
        return ranking

    def serialize(self):
        res = {}
        board = [[ "" for x in range(0,self.length)] for y in range(0,self.height)]
        for x in range(0,self.length):
            for y in range(0,self.height):
                if self.board[x][y] != None:
                    board[x][y] = self.board[x][y].serialize()
        ratable = {}
        for player in self.players.values():
            if not player.alive:
                ratable[player.position] = player.name
        ranking = []
        for pos in sorted(ratable.keys()):
            ranking.append(ratable[pos])
        res["gameId"] = self.id
        res["remainingTicks"] = int(self.stateReminingTick)
        res["state"] = int(self.state)
        res["board"] = board
        res["ranking"] = ranking
        return res
