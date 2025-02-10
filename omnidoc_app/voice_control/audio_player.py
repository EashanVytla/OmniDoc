import os
import pygame

def play_audio(file_path):
    """
    Audio playback function using pygame
    """
    try:
        # Convert to absolute path
        file_path = os.path.abspath(file_path)
        
        if not os.path.exists(file_path):
            print(f"Error: Audio file not found at {file_path}")
            return False

        # Initialize pygame mixer
        pygame.mixer.init()
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
        
        # Wait for playback to finish
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
            
        # Cleanup
        pygame.mixer.music.stop()
        pygame.mixer.quit()
        return True
        
    except Exception as e:
        print(f"Error playing audio: {e}")
        try:
            pygame.mixer.quit()
        except:
            pass
        return False

__all__ = ['play_audio']
