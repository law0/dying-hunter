# coding: utf-8

import math
import time
from enum import IntEnum
from operator import itemgetter

from game.server import *
from game.arena import *

class TournamentState(IntEnum):
    PROGRAMMED = 0
    SUBSCRIPTION = 1
    COMPUTING = 2
    READY = 3
    STARTED = 4
    ENDED = 5

class TournamentManager:
    #We need at leat 3 teams !!!

    def __init__(self):
        self.state = TournamentState.PROGRAMMED
        self.players = {}
        self.matchs = []
        self.matchArenas = []
        self.currentArena = None
        self.nextMatch = 0

    def setServer(self, game):
        self.game = game

    def dump(self):
        self.state = TournamentState.PROGRAMMED
        self.players = {}
        self.matchs = []
        self.matchArenas = []
        self.currentArena = None
        self.nextMatch = 0

    def openSubscription(self):
        self.state = TournamentState.SUBSCRIPTION

    def addPlayer(self, name):
        if self.state != TournamentState.SUBSCRIPTION:
            return False
        if not name in self.players.keys():
            self.players[name] = 0
            return True
        else:
            return False

    def closeSubscription(self):
        self.state = TournamentState.COMPUTING
        self.computeMatchs()
        self.state = TournamentState.READY

    def startTournament(self):
        self.state = TournamentState.STARTED

    def getSummaryView(self):
        view = []
        for i in range(0,len(self.matchs)):
            state = "TODO"
            winner = ""
            arenaId = self.matchArenas[i]
            if i < self.nextMatch-1:
                state = "DONE"
                winner = self.game.getArena(arenaId).getWinner()
                if winner == None:
                    winner = ""
            elif i == self.nextMatch-1:
                state = "RUNNING"
            view.append((state,winner,arenaId))
        return view

    def computeRanking(self):
        for player in self.players.keys():
            self.players[player] = 0
        end = min(self.nextMatch,len(self.matchs))
        for i in range(0,end):
            arenaId = self.matchArenas[i]
            ranking = self.game.getArena(arenaId).getRanking()
            if ranking != None:
                self.players[ranking[0]] += 5
                self.players[ranking[1]] += 3
                self.players[ranking[2]] += 1

    def getRankingView(self):
        ranking = []
        for player in self.players.keys():
            ranking.append((player, self.players[player]))
        ranking = sorted(ranking, key=itemgetter(1), reverse=True) #sort by score
        return ranking

    def computeMatchs(self):
        nbPlayers = len(self.players.keys())
        matchDuration = ArenaConstants.c_runDuration*nbPlayers+ArenaConstants.c_pauseDuration*(nbPlayers-1)
        MaxTournamentDuration = 60*30
        nbMatch = int(math.floor(MaxTournamentDuration/matchDuration))
        size = max(int(nbPlayers/2), 6)
        for i in range(nbMatch):
            self.matchs.append(list(self.players.keys()))
            arenaId = self.game.addArena(size,size)
            self.matchArenas.append(arenaId)
            arena = self.game.getArena(arenaId)
            for player in self.players.keys():
                arena.addPlayer(player)

    def setupNextMatch(self):
        if self.state != TournamentState.STARTED:
            return False
        if self.nextMatch >= len(self.matchs):
            return False
        arenaId = self.matchArenas[self.nextMatch]
        self.currentArena = self.game.getArena(arenaId)
        self.nextMatch +=1
        return True

    def startNextMatch(self):
        if self.state != TournamentState.STARTED:
            return False
        if self.nextMatch >= len(self.matchs):
            return False
        self.currentArena.startGame()
        return True


    def localTestRun(self):
        testPlayers = ["Dummy", "Fake", "Troll", "Rapid", "FCE", "Parrot"]
        directions = ["UP", "LEFT", "DOWN", "RIGHT"]
        self.openSubscription()
        for player in testPlayers:
            self.addPlayer(player)
        self.closeSubscription()
        self.startTournament()
        doContinue = True
        while doContinue:
            doContinue = setupNextMatch() and self.startNextMatch()
            while self.currentArena.state != State.ENDED:
                for player in testPlayers:
                    if self.currentArena.getPlayer(player).alive:
                        self.currentArena.move(player, random.choice(directions))
                time.sleep(1)
            time.sleep(1)
            self.computeRanking()
