import time
import pygame
import sys
import os
from datetime import datetime
import threading

pygame.init()
pygame.mixer.init()

class CustomTimer:
    def __init__(self):
        # Initialize pygame for sound playback
        pygame.init()
        pygame.mixer.init()
        self.is_running = False
        self.current_timer = None
        self.custom_sound_file = None
        self.use_custom_sound = False
        self.current_sound = None
        self.sound_playing = False  # Flag to track if sound is playing

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
            print("Using default sound instead.")
            self.use_custom_sound = False
            return False

    def play_sound(self):
        try:
            if self.current_sound and self.sound_playing:
                self.current_sound.stop()
                self.sound_playing = False

            if self.use_custom_sound and self.custom_sound_file:
                self.current_sound = pygame.mixer.Sound(self.custom_sound_file)
                self.current_sound.play()
                self.sound_playing = True
            else:
                self.play_default_sound()
        except Exception as e:
            print(f"Error playing sound: {e}")
            print('\a')

    def play_default_sound(self):
        try:
            if self.current_sound and self.sound_playing:
                self.current_sound.stop()
                self.sound_playing = False
            default_sound = pygame.mixer.Sound("japanese_high_school (online-audio-converter.com).wav")
            self.current_sound = default_sound
            self.current_sound.play()
            self.sound_playing = True
        except Exception as e:
            print(f"Error playing default sound: {e}")
            print('\a')  # Fallback system beep

    def stop_current_sound(self):
        """Immediately stop the currently playing sound."""
        if self.current_sound and self.sound_playing:
            self.current_sound.stop()
            self.sound_playing = False
            print("Current sound stopped.")
        elif not self.is_running:
            print("No timer is running, so no sound to stop.")
        elif not self.sound_playing:
            print("No sound is currently playing.")

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
    print("(Using default sound)")

    try:
        while True:
            print("\n1. Start timer")
            print("2. Stop timer")
            print("3. Set custom sound")
            print("4. Reset to default sound")
            print("5. Stop current sound (timer continues)")
            print("6. Exit")

            choice = input("\nEnter your choice (1-6): ")

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
                print("Reset to default sound")
            elif choice == '5':
                timer.stop_current_sound()
            elif choice == '6':
                print("Exiting program.")
                timer.stop_timer()
                pygame.quit()
                sys.exit()
            else:
                print("Invalid choice. Please enter a number between 1 and 6.")
    except KeyboardInterrupt:
        print("\nProgram interrupted.")
        timer.stop_timer()
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main()
