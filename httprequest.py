import requests
from threading import Thread
from Queue import Queue
from time import sleep
import json

BASE_URL = "http://localhost/"

class StatusReq:
    def __init__(self, room, timestamp, occupied):
        self.room = room
        self.timestamp = timestamp
        self.occupied = occupied

    def to_json(self):
        return json.dumps({"room":self.room, "timestamp":self.timestamp, "occupied": self.occupied})

class HttpRequest(Thread):
    def __init__(self):
        super(HttpRequest, self).__init__()
        self.queue = Queue()
        self.running = True

    def run(self):
        while self.running:
            if not self.queue.empty():
                q = self.queue.get()
                self.queue.task_done()
                requests.post(BASE_URL+q.PATH, params=q.to_json())
            sleep(0.3)
    
    def add(self, req):
        self.queue.put(req)
    
    def stop(self):
        self.running = False