import tuio
import copy
import pygame
tracking1 = tuio.Tracking(port=3341)
server = tuio.TuioServer(port=3333)
print "Starting..."


tela = pygame.display.set_mode((400, 400))
tela.fill((255, 255, 255))

try:
    while 1:
	tela.fill((255, 255, 255))
        server.cursors = {}
        tracking1.update()
        for cursor in tracking1.cursors():
        # Shows a square 5x5, on the appropriate coordinates
            tela.blit(pygame.Surface((5,5)),((int(400*cursor.xpos)), (int(400*cursor.ypos))))
            server.cursors[cursor.sessionid*2] = cursor

        pygame.display.update()
        server.update()

except KeyboardInterrupt:
    tracking1.stop()
