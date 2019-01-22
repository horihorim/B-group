import requests
from threading import Thread
try:
    import queue
except ImportError:
    import Queue as queue
import time
import json
import socket

USER_NAME = "ZbygMtA8jKGDf2sDIW6xSZnUxdjv8rRH3jt1ZT9l"
LIGHT_ID = 2

COLOR_RED = 0
COLOR_GREEN = 25500
COLOR_BLUE = 46920
MSEARCH_REQUEST_LINES = ('M-SEARCH * HTTP/1.1', 'HOST: 239.255.255.250:1900',
                         'MAN: "ssdp:discover"', 'MX: {}',
                         'ST:upnp:rootdevice', '', '')


def checkSSDPResponse(resp):
    s = resp.decode('utf-8')
    return s.find('hue-bridgeid') > 0


def findHue(timeout=5):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(timeout)
    req = bytes(
        '\r\n'.join(MSEARCH_REQUEST_LINES).format(timeout), encoding='utf-8')
    sock.sendto(req, ('239.255.255.250', 1900))
    while True:
        try:
            res, device = sock.recvfrom(4096)
            if checkSSDPResponse(res):
                sock.close()
                return device[0]
        except socket.timeout:
            sock.close()
            return None


class LightState:
    def __init__(self, hue=COLOR_GREEN, on=True, bri=80, alert="none"):
        self.on = on
        self.bri = bri
        self.hue = hue
        self.alert = alert

    def toDict(self):
        return {
            "on": self.on,
            "bri": self.bri,
            "hue": self.hue,
            "alert": self.alert
        }


class Hue:
    def __init__(self, ip, user):
        self.ip = ip
        self.user = user

    def changeState(self, lightID, state):
        url = "http://{}/api/{}/lights/{}/state".format(
            self.ip, self.user, lightID)
        resp = requests.put(
            url,
            data=json.dumps(state.toDict()),
            headers={'content-type': 'application/json'})
        return resp.status_code == requests.codes.ok


class MeetingStart:
    def exec(self, ip):
        hue = Hue(ip=ip, user=USER_NAME)
        return hue.changeState(
            lightID=LIGHT_ID, state=LightState(hue=COLOR_GREEN))


class MeetingEnd:
    def exec(self, ip):
        hue = Hue(ip=ip, user=USER_NAME)
        return hue.changeState(lightID=LIGHT_ID, state=LightState(on=False))


class MeetingTimeout:
    def exec(self, ip):
        hue = Hue(ip=ip, user=USER_NAME)
        ret = hue.changeState(
            lightID=LIGHT_ID, state=LightState(hue=COLOR_RED, alert="lselect"))
        time.sleep(10)
        ret = hue.changeState(lightID=LIGHT_ID, state=LightState(alert="none"))
        ret = hue.changeState(
            lightID=LIGHT_ID, state=LightState(hue=COLOR_GREEN))
        return ret


class HueThread(Thread):
    def __init__(self, ip):
        Thread.__init__(self)
        self.running = True
        self.queue = queue.Queue()
        self.ip = ip

    def run(self):
        while self.running:
            if not self.queue.empty():
                com = self.queue.get(block=True, timeout=0.1)
                com.exec(self.ip)

    def stop(self):
        self.running = False

    def changeState(self, com):
        self.queue.put(com)


if __name__ == "__main__":
    #ip = findHue(timeout=5)
    #if ip == None:
    #    print("can't find hue")
    #    import sys
    #    sys.exit(1)
    t = HueThread(ip="192.168.10.2")
    t.start()
    t.changeState(MeetingStart())
    time.sleep(10)
    t.changeState(MeetingTimeout())
    time.sleep(10)
    t.changeState(MeetingEnd())
    time.sleep(10)
    t.stop()
    t.join()
