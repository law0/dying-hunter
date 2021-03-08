# coding: utf-8

from multiprocessing import Process
import json
import socket

class Connection:

    def __init__(self, game, client):
        self.game = game
        self.PlayerName = None
        self.client = client

    def run(self):
        try:
            while True:
                cmd = self.client.recv(12).decode('utf-8')
                if len(cmd) == 0:
                    self.client.close()
                    break
                res = "KO"
                if self.handleCmd(cmd.strip()):
                    res = "OK"
                self.client.sendall(res.encode('utf-8'))
        except Exception as e:
            print(e)
            self.client.close()

    def handleCmd(self, cmd):
        if cmd.startswith("HELLO"):
            return self.setupPlayer(cmd.split(":")[1])
        if cmd.startswith("MOVE"):
            return self.handleMove(cmd.split(":")[1])
        if cmd.startswith("VIEW"):
            view = self.handleView()
            if view == None:
                return False
            self.client.sendall("LG".encode('utf-8'))
            self.client.sendall('{0:04d}'.format(len(view)).encode('utf-8'))
            self.client.sendall(view.encode('utf-8'))
            return True
        return False

    def setupPlayer(self, name):
        self.PlayerName = name
        return self.game.connectPlayer(self.PlayerName)

    def handleMove(self, direction):
        return self.game.addMoveRequest(self.PlayerName, direction)

    def handleView(self):
        view = self.game.getPlayerView(self.PlayerName)
        if view == None:
            return None
        jsonView = json.dumps(view)
        return jsonView

class NetworkManager:

    def __init__(self, game):
        self.game = game

    def start(self):
        p = Process(target=self.run, args=())
        p.start()

    def start(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        srvAddr = ('localhost', 8082)
        sock.bind(srvAddr)
        sock.listen(1)
        while True:
            client, client_address = sock.accept()
            connection = Connection(self.game, client)
            p = Process(target=connection.run, args=())
            p.start()
        pass
