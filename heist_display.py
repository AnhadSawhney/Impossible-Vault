import pygame
import codegen
import random

keythread = codegen.keyT(codegen.keys, True)
keythread.start()

pygame.init()
pygame.mixer.init()
pygame.mixer.music.load("radiation.wav")
pygame.mixer.music.set_volume(1)
screen = pygame.display.set_mode((512, 512), pygame.RESIZABLE)
clock = pygame.time.Clock()

counter, text = 10, "10".rjust(3)
pygame.time.set_timer(pygame.USEREVENT, 1000)
font = pygame.font.SysFont("Consolas", 30)
text = ""
input_active = True
key_success = False
started = False

radiation_duration = 64  # seconds
radiation_delay = 300  # seconds
counter = 0

run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.USEREVENT:
            counter += 1
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
        screen.blit(
            font.render("Success! Reactor deactivated", True, (0, 0, 255)), (32, 96)
        )
    elif counter > radiation_delay:
        if not started:
            pygame.mixer.music.play()
            started = True

        screen.fill((0, 0, 0))
        # draw 100 random lines across the screen, whose endpoints lie on the border

        for i in range(200):
            x1 = random.randint(0, screen.get_width())
            y1 = random.randint(0, screen.get_height())
            x2 = random.randint(0, screen.get_width())
            y2 = random.randint(0, screen.get_height())
            pygame.draw.line(screen, (255, 0, 0), (x1, y1), (x2, y2))

        screen.blit(font.render("Harmful radiation!", True, (255, 255, 255)), (32, 48))
        screen.blit(
            font.render(
                "Ends in: "
                + str(radiation_duration - (counter - radiation_delay))
                + " seconds",
                True,
                (255, 255, 255),
            ),
            (32, 96),
        )
        screen.blit(font.render("Enter key: " + text, True, (0, 0, 255)), (32, 128))
    else:  # normal operation
        started = False
        screen.fill((0, 0, 0))
        screen.blit(
            font.render(
                "Radiation in: " + str(radiation_delay - counter) + " seconds",
                True,
                (0, 0, 255),
            ),
            (32, 96),
        )
        screen.blit(font.render("Enter key: " + text, True, (0, 0, 255)), (32, 128))

    pygame.display.flip()
    clock.tick(60)

keythread.stop_looping()
keythread.join()
