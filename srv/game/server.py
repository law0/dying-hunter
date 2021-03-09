# coding: utf-8

from game.arena import *
from game.tournamentManager import *
from game.playerManager import *
from multiprocessing import Process

from enum import IntEnum

class ServerMode(IntEnum):
    DEMO = 0
    PG_BOTS = 1
    PG_EMPTY = 2
    MATCH = 3
    TOURNAMENT = 4
    TRAINING = 5

    def fromString(str):
        if str == "demo":
            return ServerMode.DEMO
        elif str == "pgbots":
            return ServerMode.PG_BOTS
        elif str == "pgempty":
            return ServerMode.PG_EMPTY
        elif str == "match":
            return ServerMode.MATCH
        elif str == "training":
            return ServerMode.TRAINING
        return ServerMode.TOURNAMENT

    def toString(mode):
        if mode == ServerMode.DEMO:
            return "demo"
        elif mode == ServerMode.PG_BOTS:
            return "pgbots"
        elif mode == ServerMode.PG_EMPTY:
            return "pgempty"
        elif mode == ServerMode.MATCH:
            return "match"
        elif mode == ServerMode.TRAINING:
            return "training"
        return "tournament"

class Server:

    def __init__(self):
        self.arenas = {}
        self.nextArenaId=0
        self.playerManager = PlayerManager()
        self.tournamentManager = TournamentManager()
        self.tournamentManager.setServer(self)
        self.mode = None
        self.changeMode(ServerMode.DEMO)

    def addArena(self, length, height):
        self.arenas[self.nextArenaId] = Arena(self.nextArenaId, length, height)
        result = self.nextArenaId
        self.nextArenaId += 1
        return result

    def addPlaygroundArena(self, length, height):
        playground = Arena(self.nextArenaId, length, height)
        playground.setPlayground()
        self.arenas[self.nextArenaId] = playground
        result = self.nextArenaId
        self.nextArenaId += 1
        return result

    def getArena(self, id):
        return self.arenas[id]

    def getArenaList(self):
        return list(self.arenas.keys())

    def getTournamentManager(self):
        return self.tournamentManager

    def connectPlayer(self, name):
        if self.mode == ServerMode.TOURNAMENT:
            if self.tournamentManager.state == TournamentState.SUBSCRIPTION:
                if not self.tournamentManager.addPlayer(name):
                    print("Subscription of "+name+" refused : name already taken")
                    return False
            else:
                if not self.tournamentManager.isPlayer(name):
                    print("Connection of "+name+" refused : not found")
                    return False
        return self.playerManager.connectPlayer(name, False)

    def addMoveRequest(self, name, direction):
        return self.playerManager.addMoveRequest(name, direction)

    def getPlayerView(self, name):
        return self.playerManager.getPlayerView(name)

    def performTick(self):
        if self.mode == ServerMode.TRAINING:
            return
        for arena in self.arenas.values():
            arena.performTick()
        self.playerManager.performTick()
        self.tournamentManager.performTick()

    def performTrainingTick(self):
        if self.mode != ServerMode.TRAINING:
            return
        for arena in self.arenas.values():
            arena.performTick()
        self.playerManager.performTick()

    def dump(self):
        self.playerManager.dump()
        self.tournamentManager.dump()
        for arena in self.arenas.values():
            arena.dump()
        self.arenas = {}
        self.nextArenaId=0

    def handleTrainingCmds(self, cmd):
        if self.mode != ServerMode.TRAINING:
            print("Reject training commands {} while not in training mode".format(cmd))
            return None
        if cmd == "addTrainingDummy":
            dummyName = "DU_"+str(len(self.playerManager.arena.players))
            self.playerManager.arena.addPlayer(dummyName)
            return None
        if cmd == "doTrainingTick":
            self.performTrainingTick()
            return None
        if cmd.startswith("trainingMove"):
            name = cmd.split()[1]
            x = int(cmd.split()[2])
            y = int(cmd.split()[3])
            self.playerManager.arena.setPosition(name, x, y)
            return None
        if cmd.startswith("trainingSetHunter"):
            name = cmd.split()[1]
            self.playerManager.arena.setHunter(name)
        if cmd.startswith("trainingSetFrozen"):
            name = cmd.split()[1]
            self.playerManager.arena.setFrozen(name)
        if cmd.startswith("trainingSetSafe"):
            name = cmd.split()[1]
            self.playerManager.arena.setSafe(name)
        if cmd.startswith("trainingSetNormal"):
            name = cmd.split()[1]
            self.playerManager.arena.setNormal(name)

        return None

    def handleServerCmds(self, cmd):
        if cmd.startswith("setMode"):
            self.changeMode(ServerMode.fromString(cmd.split()[1]))
            return None
        if cmd.startswith("getServerView"):
            return self.getServerView()
            return None
        if cmd == "startPG":
            if self.mode == ServerMode.DEMO:
                self.setupPlayground(True)
                self.runArena()
                return None
            else:
                self.setupPlayground(self.mode == ServerMode.PG_BOTS)
                return None
        if cmd == "startMatch":
            self.setupMatch()
            return None
        if cmd == "stopPG":
            self.dump()
            return None
        if cmd == "startTournament":
            if self.mode == ServerMode.TOURNAMENT:
                self.setupTournament()
            return None
        if cmd == "closeSubs":
            if self.mode == ServerMode.TOURNAMENT:
                self.launchTournament()
            return None
        if cmd == "startNextGame":
            if self.mode == ServerMode.TOURNAMENT:
                self.launchTournamentNextMatch()
            else:
                self.runArena()
            return None
        #TODO remove try catch
        try:
            res = self.handleTrainingCmds(cmd)
        except Exception as e:
            print(e)
        return res

    def changeMode(self, mode):
        if mode == self.mode:
            return
        self.dump()
        self.mode = mode

    def getServerView(self):
        view = {}
        view["mode"] = ServerMode.toString(self.mode)
        if self.mode == ServerMode.TOURNAMENT:
            if self.tournamentManager.state == TournamentState.PROGRAMMED:
                view["CurServerStep"] = "stopped"
                view["CurGameStatus"] = "none"
            elif self.tournamentManager.state == TournamentState.SUBSCRIPTION:
                view["CurServerStep"] = "subscription"
                view["CurGameStatus"] = "none"
            elif self.tournamentManager.state == TournamentState.COMPUTING or self.tournamentManager.state == TournamentState.READY:
                view["CurServerStep"] = "running"
                view["CurGameStatus"] = "none"
            elif self.tournamentManager.state == TournamentState.STARTED:
                view["CurServerStep"] = "running"
                if self.tournamentManager.currentArena == None :
                    view["CurGameStatus"] = "none"
                elif self.tournamentManager.currentArena.state == State.ENDED:
                    view["CurGameStatus"] = "ended"
                elif self.tournamentManager.currentArena.state == State.PENDING:
                    view["CurGameStatus"] = "pending"
                else:
                    view["CurGameStatus"] = "running"
            else:
                view["CurServerStep"] = "stopped"
                view["CurGameStatus"] = "ended"
        else:
            if len(self.arenas) == 0:
                view["CurServerStep"] = "stopped"
                view["CurGameStatus"] = "none"
            elif self.arenas[0].state == State.ENDED:
                view["CurServerStep"] = "started"
                view["CurGameStatus"] = "ended"
            elif self.arenas[0].state == State.PENDING:
                view["CurServerStep"] = "pending"
                view["CurGameStatus"] = "pending"
            else:
                view["CurServerStep"] = "started"
                view["CurGameStatus"] = "running"
        return view

    def setupPlayground(self, withBots):
        id = self.addPlaygroundArena(6,6)
        arena = self.getArena(id)
        self.playerManager.setArena(arena)
        if withBots:
            self.playerManager.addBot("Dummy")
            self.playerManager.addBot("Faker")
            self.playerManager.addBot("Troll")

    def setupMatch(self):
        id = self.addArena(6,6)
        arena = self.getArena(id)
        self.playerManager.setArena(arena)

    def runArena(self):
        self.playerManager.arena.startGame()

    def setupTournament(self):
        self.playerManager.setArena(self.tournamentManager.pendingArena)
        self.tournamentManager.openSubscription()

    def launchTournament(self):
        self.tournamentManager.closeSubscription()
        self.tournamentManager.startTournament()

    def launchTournamentNextMatch(self):
        self.tournamentManager.setupNextMatch()
        self.playerManager.setArena(self.tournamentManager.currentArena)
        self.tournamentManager.startNextMatch()
