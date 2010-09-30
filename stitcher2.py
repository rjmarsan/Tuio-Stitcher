
import math
import tuio
import copy

class Tracker:
    def __init__(self, port, rotation = 0, scale = (0.5, 1.0), shift = (0, 0)):
        self.port = port
        self.tracker = tuio.Tracking(port = port)
        self.rotation = rotation
        self.scale = scale
        self.shift = shift

    def distance(self, cursor):
        return math.sqrt(cursor.xpos ** 2 + cursor.ypos ** 2)

    def rotate_cursor(self, cursor):
        dst = self.distance(cursor)
        angle = math.atan2(cursor.ypos, cursor.xpos)
        angle = angle + self.rotation
        cursor.xpos = math.cos(angle) * dst
        cursor.ypos = math.sin(angle) * dst

    def transform_cursor(self, cursor):
        """Switch x and y coords to rotate."""
        t = cursor.xpos
        cursor.xpos = cursor.ypos
        cursor.ypos = t

    def scale_cursor(self, cursor):
        (xscale, yscale) = self.scale
        cursor.xpos = cursor.xpos * xscale
        cursor.ypos = cursor.ypos * yscale

    def shift_cursor(self, cursor):
        (deltax, deltay) = self.shift
        cursor.xpos = cursor.xpos + deltax
        cursor.ypos = cursor.ypos + deltay

    def normalize_cursor(self, incursor):
        outcursor = copy.copy(incursor)
        self.transform_cursor(outcursor)
        self.rotate_cursor(outcursor)
        self.scale_cursor(outcursor)
        self.shift_cursor(outcursor)
        return outcursor

    def cursors(self):
        self.tracker.update()
        for cursor in self.tracker.cursors():
            yield self.normalize_cursor(cursor)

class Server:
    def __init__(self, outport, trackers, threshold = 0.004, cleanupticks = 10):
        """Threshold is the distance (as a percentage) withinwhich two cursors are the same."""
        self.server = tuio.TuioServer(port = outport)
        self.trackers = trackers

        self.threshold = threshold
        self.cleanupticks = cleanupticks
        self.nextid = 1
        self.tick = 1
        self.cursormap = {} # (port, id) -> (server's id, last used tick)

    def match_cursor(self, tracker, cursor):
        (srvid, lastused) = self.cursormap[(tracker.port, cursor.sessionid)]
        self.cursormap[(tracker.port, cursor.sessionid)] = (srvid, self.tick)
        if self.server.cursors[srvid].lastused == self.tick:
            # already updated this cursor, ignore
            print "Duplicate cursor %d on port %d for %d ignored" % (cursor.sessionid, tracker.port, srvid)
            pass
        else:
            #print "Updating %d as %d on port %d" % (srvid, cursor.sessionid, tracker.port)
            cursor.lastused = self.tick
            cursor.sessionid = srvid
            cursor.tracker = tracker.port
            self.server.cursors[srvid] = cursor

    def close_enough(self, cursor1, cursor2):
        return (abs(cursor1.xpos - cursor2.xpos) < self.threshold and
                abs(cursor1.ypos - cursor2.ypos) < self.threshold)

    def new_id(self):
        i = self.nextid
        self.nextid = self.nextid + 1
        return i

    def merge_cursor(self, tracker, cursor):
        """Add an entry in cursormap for cursor, inserting into the server if necessary."""
        for srvcursor in self.server.cursors.itervalues():
            # make sure this cursor was used very recently
            if srvcursor.tracker != tracker.port and srvcursor.lastused > self.tick - 100 and self.close_enough(srvcursor, cursor):
                # should be same cursor
                self.cursormap[(tracker.port, cursor.sessionid)] = (srvcursor.sessionid, self.tick)
                print "Mapped %d on port %d to %d" % (cursor.sessionid, tracker.port, srvcursor.sessionid)
                return
        # no match found, have to add one
        newid = self.new_id()
        print "Adding %d on port %d as %d" % (cursor.sessionid, tracker.port, newid)
        self.cursormap[(tracker.port, cursor.sessionid)] = (newid, self.tick)
        cursor.sessionid = newid
        cursor.lastused = self.tick
        cursor.tracker = tracker.port
        self.server.cursors[newid] = cursor


    def cleanup(self):
        if self.tick % self.cleanupticks == 0:
            for (k, v) in self.cursormap.items():
                (port, trackid) = k
                (srvid, lastused) = v
                if lastused < self.tick - self.cleanupticks:
                    del self.cursormap[k]
            for (srvid, cursor) in self.server.cursors.items():
                if cursor.lastused < self.tick - self.cleanupticks:
                    del self.server.cursors[srvid]
            if len(self.server.cursors) != 0:
            	print "Cleanup: %d cursors, %d mappings" % (len(self.server.cursors), len(self.cursormap))

    def update(self):
        self.tick = self.tick + 1
        for tracker in self.trackers:
            for cursor in tracker.cursors():
                if (tracker.port, cursor.sessionid) in self.cursormap:
                    self.match_cursor(tracker, cursor)
                else:
                    self.merge_cursor(tracker, cursor)
        self.cleanup()
        self.server.update()

if __name__ == "__main__":
    tracker1 = Tracker(3340)
    tracker2 = Tracker(3341, shift = (0.4, 0))
    server = Server(3333, [tracker1, tracker2])

    while 1:
        server.update()
