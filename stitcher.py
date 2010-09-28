

import tuio
import copy

class Tracker:
  def __init__(self, port, rotation = 0, scale = (0.5, 1.0), shift = (0, 0)):
    self.port = port
    self.tracker = tuio.Tracking(port = port)
    self.rotation = rotation
    self.scale = scale
    self.shift = shift

  def distance(self, point1, point2):
    (x1, y1) = point1
    (x2, y2) = point2
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

  def rotate(self, cursor):
    dst = self.distance((0, 0), (cursor.xpos, cursor.ypos))
    angle = math.atan2(cursor.ypos, cursor.xpos)
    angle = angle + self.rotation
    cursor.xpos = math.cos(angle) * dst
    cursor.ypos = math.sin(angle) * dst

  def transform(self, cursor):
    """Switch x and y coords to rotate."""
    t = cursor.xpos
    cursor.xpos = cursor.ypos
    cursor.ypos = t

  def scale(self, cursor):
    (xscale, yscale) = self.scale
    cursor.xpos = cursor.xpos * xscale
    cursor.ypos = cursor.ypos * yscale

  def shift(self, cursor):
    (deltax, deltay) = self.shift
    cursor.xpos = cursor.xpos + deltax
    cursor.ypos = cursor.ypos + deltay

  def normalize(self, incursor):
    outcursor = copy.copy(incursor)
    self.transform(outcursor)
    self.rotate(outcursor)
    self.scale(outcursor)
    self.shift(outcursor)
    return outcursor

  def cursors(self):
    self.tracker.update()
    for cursor in self.tracker.cursors():
      yield self.normalize(cursor)

class Server:
  def __init__(self, outport, trackers, threshold = 0.03):
    """Threshold is the distance (as a percentage) withinwhich two cursors are the same."""
    self.server = tuio.TuioServer(port = outport)
    self.trackers = trackers
    self.threshold = threshold
    self.nextid = 1
    self.tick = 1
    self.cursormap = {} # (port, id) -> (server's id, last used tick)

  def update(self):
    self.tick = self.tick + 1
    for tracker in trackers:
      for cursor in tracker.cursors():
        if (tracker.port, cursor.sessionid) in self.cursormap:
          (srvid, lastused) = self.cursormap[(tracker.port, cursor.sessionid)]
          self.cursormap[(tracker.port, cursor.sessionid)] = (srvid, self.tick)
          if self.server.cursors[srvid].lastused == self.tick:
            # already updated this cursor, ignore
            pass
          else:
            cursor.lastused = self.tick
            self.server.cursors[srvid] = cursor





      
#TODO: match same cursors
#TODO: resolve duplicates
#TODO: clean up old duplicate mappings [LRU method]

