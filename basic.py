import tuio
import copy
tracking1 = tuio.Tracking(port=3341)
server = tuio.TuioServer(port=3333)
print "Starting..."


def transform(cursor):
    return cursor


try:
    while 1:
        server.cursors = {}
        tracking1.update()
        for cursor in tracking1.cursors():
            server.cursors[cursor.sessionid*2] = transform(cursor)
        server.update()
except KeyboardInterrupt:
    tracking1.stop()
