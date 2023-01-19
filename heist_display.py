import pygame
import codegen
import audiostream
import random
import sounddevice as sd
import numpy as np

keythread = codegen.keyT(codegen.keys, True)
keythread.start()

MAXVOL = 7
streamthread = audiostream.StreamT(MAXVOL)
streamthread.start()

pygame.init()
pygame.mixer.init()
pygame.mixer.music.load("alarm.mp3")
pygame.mixer.music.set_volume(.5)
screen = pygame.display.set_mode((1024, 512), pygame.RESIZABLE)
clock = pygame.time.Clock()

counter, text = 10, "10".rjust(3)

pygame.time.set_timer(pygame.USEREVENT, 250) # game loop runs every .25 sec 
font = pygame.font.SysFont("Consolas", 30)
text = ""
input_active = True
key_success = False
started = False

radiation_duration = 10  # seconds
radiation_delay = 300  # seconds
counter = 0
current_vol = 0
game_over = False

''' ignore this
fs = 44100 
sd.default.samplerate = 44100
sd.default.channels = 2

def record(): # calculate current volume by recording a snippet
    duration = .7  # seconds
    myrecording = sd.rec(int(duration * fs))
    print("recording...")
    sd.wait()
    volume_norm = np.linalg.norm(myrecording)*5
    print(volume_norm)
    return volume_norm
'''

run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.USEREVENT:
            #current_vol = record() # take current vol
            current_vol = audiostream.get_last_vol(streamthread)  # take current vol
            counter += .25
            if counter > radiation_duration + radiation_delay:
                counter = 0
        elif event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.KEYDOWN and input_active:
            if event.key == pygame.K_RETURN:
                input_active = False
            elif event.key == pygame.K_BACKSPACE:
                text = text[:-1]
            else:
                text += event.unicode

    if not input_active:
        input_active = True
        if text.lower() == keythread.k.lower():
            print("Success: correct key entered")
            key_success = True
        else:
            print("Key incorrect")
            text = ""

    if key_success:
        screen.fill((0, 255, 0))
        x, y = screen.get_size()
        screen.blit(
            font.render("DOWNLOAD SUCCESSFULLY COMPLETED", True, (0, 0, 255)), (x*2/5, y*3/4)
        )


    elif counter > radiation_delay or current_vol > MAXVOL or game_over == True:
        game_over = True
        screen.fill((130, 0, 0))
        
        if not started:
            pygame.mixer.music.play()
            started = True

        #screen.fill((0, 0, 0))
        # draw 100 random lines across the screen, whose endpoints lie on the border

        for i in range(200):
            x1 = random.randint(0, screen.get_width())
            y1 = random.randint(0, screen.get_height())
            x2 = random.randint(0, screen.get_width())
            y2 = random.randint(0, screen.get_height())
            pygame.draw.line(screen, (255, 0, 0), (x1, y1), (x2, y2))

        screen.blit(font.render("Alarms sounded!", True, (255, 255, 255)), (32, 48))
        '''screen.blit(
            font.render(
                "Ends in: "
                + str(radiation_duration - (counter - radiation_delay))
                + " seconds",
                True,
                (255, 255, 255),
            ),
            (32, 96),
        )
        screen.blit(font.render("Enter key: " + text, True, (0, 0, 255)), (32, 128))'''
    else:  # normal operation
        started = False
        screen.fill((0, 0, 0))
        screen.blit(
            font.render(
                "Radiation in: " + str(radiation_delay - int(counter)) + " seconds",
                True,
                (0, 0, 255),
            ),
            (32, 96),
        )
        screen.blit(font.render("Enter key: " + text, True, (0, 0, 255)), (32, 128))
        screen.blit(font.render("Current Volume: " + '|'*int(current_vol**1.8), True, (0, 0, 255)), (32, 228))

    pygame.display.flip()
    clock.tick(30)



keythread.stop_looping()
keythread.join()


if streamthread.is_alive():
    streamthread.terminate()
    streamthread.join()
