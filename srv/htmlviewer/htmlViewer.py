# coding: utf-8

import cgitb
import http.server
from multiprocessing import Process
import os
import asyncio
import websockets
import json


class GameWebsocketManager:
    def __init__(self, game):
        self.game = game

    async def handle(self, websocket, path):
        while True:
            try:
               cmd = await websocket.recv()
               if cmd == "tournamentSummary":
                   await self.handleTournamentSummary(websocket)
               elif cmd.startswith("viewArena"):
                   await self.handleViewArena(websocket, cmd.split()[1])
               else:
                   await self.handleServerCmds(websocket, cmd)
            except:
                break

    async def handleTournamentSummary(self, websocket):
        data = {}
        data["Players"] = self.game.getTournamentManager().getRankingView()
        data["Matchs"] = self.game.getTournamentManager().getSummaryView()
        jsonList = json.dumps(data)
        await websocket.send(jsonList)

    async def handleViewArena(self, websocket, id):
        jsonArena = json.dumps(self.game.getArena(int(id)).serialize())
        await websocket.send(jsonArena)

    async def handleServerCmds(self, websocket, cmd):
        res = self.game.handleServerCmds(cmd)
        if res != None:
            jsonRes = json.dumps(res)
            await websocket.send(jsonRes)

class quietServer(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

class htmlViewer:

    def __init__(self, port, gameServer):
        self.port = port
        self.game = gameServer

    def webSockMain(self, game):
        manager = GameWebsocketManager(game)
        server = websockets.serve(manager.handle, "localhost", self.port+1)
        asyncio.get_event_loop().run_until_complete(server)
        asyncio.get_event_loop().run_forever()

    def httpServerMain(self):
        server = http.server.HTTPServer

        # use handler = http.server.SimpleHTTPRequestHandler to get http logs
        handler = quietServer

        print("Viewer actif sur le port :", self.port)

        web_dir = os.path.join(os.path.dirname(__file__), 'res/html_root')
        os.chdir(web_dir)

        cgitb.enable()
        server_address = ("", self.port)
        httpd = server(server_address, handler)
        httpd.serve_forever()

    def launch(self):
        p = Process(target=self.httpServerMain, args=())
        p.start()
        p = Process(target=self.webSockMain, args=(self.game,))
        p.start()
