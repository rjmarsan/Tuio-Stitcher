# Copyright (C) 2009  Andrew Turley <aturley@acm.org>

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  US

from os import curdir, sep
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import SocketServer
import osc
import json
import socket
import math
import sys

fseq = 0

touches = {}

class Touch(object):
    def __init__(self, id):
        self.id = id
        self.x = None
        self.y = None
        self.X = None
        self.Y = None
        self.m = None
        self.time = None
    def update(self, x, y, time):
        if (self.time):
            dt = float(time - self.time) / 1000
            if not ((time - self.time) == 0):
                new_X = (x - self.x) / dt
                new_Y = (y - self.y) / dt
                dX = new_X - self.X
                dY = new_Y - self.Y
                self.m = math.sqrt((dX ** 2) + (dY ** 2))
                self.X = new_X
                self.Y = new_Y
                self.x = x
                self.y = y
                self.time = time
        else:
            self.x = float(x)
            self.y = float(y)
            self.X = 0.0
            self.Y = 0.0
            self.m = 0.0
            self.time = time

def handle_input(input, ipAddress):
    global fseq
    global touches
    for evt in input:
        if evt['elementId'] == "tuio":
            if evt['action'] == "alive":
                # remove the touches that are gone from the list
                for id in touches.keys():
                    if not id in evt['alive']:
                        del touches[id]
                # add new touches
                for id in evt['alive']:
                    if not touches.has_key(id):
                        touches[id] = Touch(id)
                osc.sendMsg("/tuio/2Dcur", ["fseq", fseq], osc_host, osc_port)
                fseq += 1
                args = ["alive"]
                args.extend([t.id for t in touches.values()])
                osc.sendMsg("/tuio/2Dcur", args, osc_host, osc_port)
            elif evt['action'] == "move":
                osc.sendMsg("/tuio/2Dcur", ["fseq", fseq], osc_host, osc_port)
                fseq += 1
                for t in evt['touches']:
                    id = t['identifier']
                    touches[id].update(float(t['x'])/surface_width, float(t['y'])/surface_height, evt['time'])
                    osc.sendMsg("/tuio/2Dcur", ["set", id, touches[id].x, touches[id].y, touches[id].X, touches[id].Y, touches[id].m], osc_host, osc_port)

class ThreadedHTTPServer(SocketServer.ThreadingMixIn, HTTPServer):
    daemon_threads = True
    pass

class MyHandler(BaseHTTPRequestHandler):
    def log_request(self, *args, **kwargs):
        return
    def do_POST(self):
        if (True):
            try:
                clen = int(self.headers.getheader('content-length'))
                incoming = self.rfile.read(clen)
                self.send_response(200)
                self.send_header('Content-type',	'text/html')
                self.end_headers()
                self.wfile.write("ok")
                incoming_parsed = json.loads(incoming)
                handle_input(incoming_parsed, self.address_string())
            except IOError:
                self.send_error(404,'File Not Found: %s' % self.path)

    def do_GET(self):
        if (self.path in ["/tuiosh.html", "/tuiosh.js", "/jquery.js", "/jquery.json.js"]):
            try:
                f = open(curdir + sep + self.path) #self.path has /test.html
                self.send_response(200)
                self.send_header('Content-type',	'text/html')
                self.end_headers()
                self.wfile.write(f.read())
                f.close()
            except IOError:
                self.send_error(404,'File Not Found: %s' % self.path)
        else:
            self.send_error(404,'File Not Found: %s' % self.path)

def main():
    try:
        # server = HTTPServer(('', http_port), MyHandler)
        server = ThreadedHTTPServer(('', http_port), MyHandler)
        print 'Running server at (%s:%d)'%(socket.gethostbyname(socket.gethostname()), http_port)
        server.serve_forever()
    except KeyboardInterrupt:
        print '^C received, shutting down server'
        server.socket.close()

if __name__ == '__main__':
    if (len(sys.argv) != 6):
        print len(sys.argv),"Usage: %s HTTP_PORT DEST_OSC_HOST DEST_OSC_PORT SURFACE_HEIGHT SURFACE_WIDTH"%(sys.argv[0])
        sys.exit()
    global http_port
    http_port = int(sys.argv[1])
    global osc_host
    osc_host = sys.argv[2]
    global osc_port
    osc_port = int(sys.argv[3])
    global surface_width
    surface_width = int(sys.argv[4])
    global surface_height
    surface_height = int(sys.argv[5])
    osc.init()
    main()
