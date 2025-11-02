import pygame

class Sound:
    pygame.mixer.init()
    start_sound = pygame.mixer.Sound('../sfx/start.wav')
    collide_sound = pygame.mixer.Sound('../sfx/collide.wav')
    collide_sound.set_volume(0.4)
    win_sound = pygame.mixer.Sound('../sfx/win.wav')
    
    @staticmethod
    def play_sound(sound):
        if sound == "start":
            Sound.start_sound.play()
        elif sound == "collide":
            Sound.collide_sound.play()
        elif sound == "win":
            Sound.win_sound.play()