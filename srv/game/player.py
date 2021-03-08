# coding: utf-8

from enum import Enum

class Role(Enum):
    PREY = 0
    HUNTER = 1

class Status(Enum):
    NORMAL = 0
    SAFE = 1
    FROZEN = 2

class Player:

    def __init__(self, name):
        self.x = 0
        self.y = 0
        self.name = name
        self.alive = True
        self.position = 0
        self.role = Role.PREY
        self.status = Status.SAFE
        self.statusTime = 0

    def serialize(self):
        #name/role/status
        res = self.name+"/"
        if self.role == Role.PREY:
            res += "P/"
        else:
            res += "H/"
        if self.status == Status.SAFE:
            res += "S"
        elif self.status == Status.FROZEN:
            res += "F"
        else:
            res += "N"
        return res
