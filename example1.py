import tuio
tracking1 = tuio.Tracking(port=3340)
tracking2 = tuio.Tracking(port=3341)
print "Starting..."

try:
    while 1:
        tracking1.update()
        tracking2.update()
        for cursor in tracking1.cursors():
            print "1: "+str(cursor)
        for cursor in tracking2.cursors():
            print "2: "+str(cursor)
except KeyboardInterrupt:
    tracking.stop()
