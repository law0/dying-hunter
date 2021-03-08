# coding: utf-8

import time
import sched
from multiprocessing import Process


class TimeManager:

    def __init__(self):
        self.sc = sched.scheduler(time.time, time.sleep)
        self.listeners = []

    def start(self):
        p = Process(target=self.run, args=())
        p.start()

    def run(self):
        self.sc.enter(1, 1, self.performTick, ())
        self.sc.run()

    def performTick(self):
        for listener in self.listeners:
            listener.performTick()
        self.sc.enter(1, 1, self.performTick, ())

    def addTickListener(self, listener):
        self.listeners.append(listener)

    def removeTickListener(self, listener):
        self.listeners.remove(listener)
