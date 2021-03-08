#!/usr/bin/env python3
# coding: utf-8


import asyncio
import sys
from multiprocessing import Manager
from multiprocessing.managers import SyncManager

from htmlviewer.htmlViewer import *
from game.networkManager import *
#from game.playerManager import *
from game.server import *
from game.timeManager import *
#from game.tournamentManager import *

def main():
    SyncManager.register('Server', Server)
    #SyncManager.register('PlayerManager', PlayerManager)
    #SyncManager.register('TournamentManager', TournamentManager)
    manager = SyncManager()
    manager.start()
    tm = TimeManager()
    game = manager.Server()
    tm.addTickListener(game)
    nm = NetworkManager(game)
    viewer = htmlViewer(8086, game)
    viewer.launch()
    tm.start()
    nm.start()
    asyncio.get_event_loop().run_forever()

if __name__ == "__main__":
    sys.exit(main())
