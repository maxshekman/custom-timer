
import time
import pygame
import sys
import os
from datetime import datetime
import threading

class CustomTimer:
    def __init__(self):
        # Initialize pygame for sound playback
        pygame.init()
        pygame.mixer.init()
        self.is_running = False
        self.current_timer = None
        self.custom_sound_file = None
        self.use_custom_sound = False
    
    def set_sound(self, sound_file):
        """Set custom sound file for the alarm"""
        try:
            # Test if sound file can be loaded
            pygame.mixer.Sound(sound_file)
            self.custom_sound_file = sound_file
            self.use_custom_sound = True
            print(f"Sound set to: {sound_file}")
            return True
        except Exception as e:
            print(f"Error setting sound: {e}")
            print("Using default beep sound instead.")
            self.use_custom_sound = False
            return False
    
    def play_sound(self):
        """Play the alarm sound"""
        try:
            if self.use_custom_sound and self.custom_sound_file:
                sound = pygame.mixer.Sound(self.custom_sound_file)
                sound.play()
                pygame.time.wait(int(sound.get_length() * 1000))
            else:
                # Generate a simple beep sound using pygame
                self._play_beep_sound()
        except Exception as e:
            print(f"Error playing sound: {e}")
            # Fall back to system beep as a last resort
            print('\a')  # ASCII bell character
    
    def _play_beep_sound(self):
        """Generate and play a simple beep sound using pygame"""
        sample_rate = 44100
        duration = 1.0  # seconds
        frequency = 440  # A4 note
        
        # Generate a square wave
        buf = pygame.mixer.Sound(buffer=b''.join(
            int(32767 * (1 if (i / sample_rate * frequency * 2) % 2 < 1 else -1)).to_bytes(2, 'little', signed=True)
            for i in range(int(sample_rate * duration))
        ))
        
        buf.play()
        pygame.time.wait(int(duration * 1000))
    
    def start_timer(self, interval_minutes):
        """Start timer with given interval in minutes"""
        if self.is_running:
            print("Timer is already running. Stop it first.")
            return
        
        self.is_running = True
        # Convert minutes to seconds for the internal timer
        interval_seconds = interval_minutes * 60
        
        def timer_thread():
            while self.is_running:
                time.sleep(interval_seconds)
                if self.is_running:  # Check if timer was stopped while sleeping
                    current_time = datetime.now().strftime("%H:%M:%S")
                    print(f"\nALARM! Time: {current_time}")
                    self.play_sound()
        
        self.current_timer = threading.Thread(target=timer_thread)
        self.current_timer.daemon = True
        self.current_timer.start()
        print(f"Timer started with interval: {interval_minutes} minutes")
        print("Press Ctrl+C to stop the timer")
    
    def stop_timer(self):
        """Stop the running timer"""
        if not self.is_running:
            print("No timer is currently running.")
            return
            
        self.is_running = False
        print("Timer stopped.")

def main():
    timer = CustomTimer()
    print("=== Custom Timer Application ===")
    print("(Using built-in beep sound by default)")
    
    try:
        while True:
            print("\n1. Start timer")
            print("2. Stop timer")
            print("3. Set custom sound")
            print("4. Reset to default beep sound")
            print("5. Exit")
            
            choice = input("\nEnter your choice (1-5): ")
            
            if choice == '1':
                try:
                    interval_minutes = float(input("Enter interval between alarms (in minutes): "))
                    timer.start_timer(interval_minutes)
                except ValueError:
                    print("Please enter a valid number for the interval.")
            elif choice == '2':
                timer.stop_timer()
            elif choice == '3':
                sound_file = input("Enter path to sound file (.wav or .mp3): ")
                timer.set_sound(sound_file)
            elif choice == '4':
                timer.use_custom_sound = False
                print("Reset to default beep sound")
            elif choice == '5':
                print("Exiting program.")
                timer.stop_timer()
                pygame.quit()
                sys.exit()
            else:
                print("Invalid choice. Please enter a number between 1 and 5.")
    except KeyboardInterrupt:
        print("\nProgram interrupted.")
        timer.stop_timer()
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main()