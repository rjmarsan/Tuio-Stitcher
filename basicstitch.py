import tuio
import copy
tracking1 = tuio.Tracking(port=3340)
tracking2 = tuio.Tracking(port=3341)
server = tuio.TuioServer(port=3333)
print "Starting..."


def transform(cursor):
    cursor = copy.copy(cursor)
    t = cursor.xpos
    cursor.xpos = cursor.ypos
    cursor.ypos = t
    cursor.xpos = cursor.xpos * 0.5
    return cursor


try:
    while 1:
        server.cursors = {}
        tracking1.update()
        tracking2.update()
        for cursor in tracking1.cursors():
            server.cursors[cursor.sessionid*2] = transform(cursor)
            print "1: ID: "+str(cursor.sessionid)+"X:"+str(cursor.xpos)+" Y:"+str(cursor.ypos)
        for cursor in tracking2.cursors():
            server.cursors[cursor.sessionid*2+1] = transform(cursor)
            print "2: ID: "+str(cursor.sessionid)+"X:"+str(cursor.xpos)+" Y:"+str(cursor.ypos)
        server.update()
except KeyboardInterrupt:
    tracking1.stop()
    tracking2.stop()
