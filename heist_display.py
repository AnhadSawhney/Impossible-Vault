import pygame
import codegen
import audiostream
import random
import sounddevice as sd
import numpy as np
import percentage_gauge
import heartrate
import linedetection
import threading

stopevent = threading.Event()

keythread = codegen.keyT(codegen.keys, True, stopevent)
keythread.start()

MAXVOL = 60
audiothread = audiostream.StreamT(MAXVOL, stopevent)
audiothread.start()

MAXHR = 100
heartthread = heartrate.HeartT(MAXHR, stopevent)
heartthread.start()

linethread = linedetection.CameraT(stopevent)
linethread.start()

pygame.init()
pygame.mixer.init()
pygame.mixer.music.load("alarm.mp3")
pygame.mixer.music.set_volume(1)
#pygame.mixer.pause()
width, height = (1024, 512)
screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
clock = pygame.time.Clock()

counter, text = 10, "10".rjust(3)

pygame.time.set_timer(pygame.USEREVENT, 100) # samples audio every .1 sec 
font = pygame.font.SysFont("Consolas", 30)
text = ""
key_success = False

counter = 0
current_vol = 0
current_hr = 0
image = None
game_over = False
started = False

volumeGauge = percentage_gauge.Gauge(
        screen=screen,
        FONT=font,
        x_cord=width / 4,
        y_cord=height / 2,
        thickness=30,
        radius=100,
        circle_colour=(55, 77, 91),
        glow=False)

heartGauge = percentage_gauge.Gauge(
        screen=screen,
        FONT=font,
        x_cord=2*width / 4,
        y_cord=height / 2,
        thickness=30,
        radius=100,
        circle_colour=(55, 77, 91),
        glow=False)

run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.USEREVENT:
            #current_vol = record() # take current vol
            current_vol = audiothread.get_last_vol()  # take current vol
            current_hr = heartthread.get_last_hr()
            line_status = linethread.is_line_broken()
            image = linethread.getImageForPygame()

            if current_vol > MAXVOL:  # check the alarms here  
                game_over = True
            if current_hr > MAXHR:
                game_over = True
            #if line_status:
            #    game_over = True

        elif event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if text.lower() == keythread.k.lower():
                    print("Success: correct key entered")
                    key_success = True
                else:
                    print("Key incorrect")
                    text = ""
            elif event.key == pygame.K_ESCAPE:
                run = False
            elif event.key == pygame.K_BACKSPACE:
                text = text[:-1]
            else:
                text += event.unicode

    if key_success:
        screen.fill((0, 255, 0))
        x, y = screen.get_size()
        screen.blit(
            font.render("DOWNLOAD SUCCESSFULLY COMPLETED", True, (0, 0, 255)), (x*2/5, y*3/4)
        )
    elif game_over == True:
        game_over = True # latch
        screen.fill((130, 0, 0))
        
        if not started:
            pygame.mixer.music.play()
            started = True # latch

        #screen.fill((0, 0, 0))
        # draw 100 random lines across the screen, whose endpoints lie on the border

        for i in range(200):
            x1 = random.randint(0, screen.get_width())
            y1 = random.randint(0, screen.get_height())
            x2 = random.randint(0, screen.get_width())
            y2 = random.randint(0, screen.get_height())
            pygame.draw.line(screen, (255, 0, 0), (x1, y1), (x2, y2))

        screen.blit(font.render("Alarms sounded!", True, (255, 255, 255)), (32, 48))
    else:  # normal operation
        screen.fill((0, 0, 0))
        screen.blit(font.render("Enter key: " + text, True, (0, 0, 255)), (32, 32))
        
        volumeGauge.draw(int(current_vol/MAXVOL*100), str(int(current_vol)), True)
        heartGauge.draw(int(current_hr/MAXHR*100), str(int(current_hr))+" BPM", True)

        #screen.blit(font.render("Current HR: " + str(current_hr) + " BPM", True, (0, 0, 255)), (32, 432))

        if image is not None:
            iwidth, iheight = image.get_size()
            new_size = (round(iwidth * 0.3), round(iheight * 0.3))
            scaled_image = pygame.transform.smoothscale(image, new_size) 
            image_rect = scaled_image.get_rect(center=(3*width/4, height/2))
            screen.blit(scaled_image, image_rect)

    pygame.display.flip()
    clock.tick(30)

pygame.quit()

print("quitting")

stopevent.set()
keythread.join()
heartthread.join()
linethread.join()
audiothread.join()
