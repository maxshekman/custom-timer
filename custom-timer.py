import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox
import time
import threading
from datetime import datetime
import pygame
import os
import sys
import platform  # To check the operating system
import subprocess  # Import the subprocess module

pygame.mixer.init()

class CustomTimer:
    def __init__(self):
        self.is_running = False
        self.current_timer = None
        self.custom_sound_file = "japanese_high_school (online-audio-converter.com).wav" # Default
        self.use_custom_sound = False
        self.current_sound = None
        self.sound_playing = False

    def set_sound(self, sound_file):
        try:
            pygame.mixer.Sound(sound_file)
            self.custom_sound_file = sound_file
            self.use_custom_sound = True
            return True
        except Exception as e:
            self.use_custom_sound = False
            return False

    def play_sound(self):
        try:
            if self.current_sound and self.sound_playing:
                self.current_sound.stop()
                self.sound_playing = False

            sound_to_play = pygame.mixer.Sound(self.custom_sound_file if self.use_custom_sound and self.custom_sound_file else "japanese_high_school (online-audio-converter.com).wav")
            self.current_sound = sound_to_play
            self.current_sound.play()
            self.sound_playing = True
        except Exception as e:
            print(f"Error playing sound: {e}")
            print('\a')

    def stop_current_sound(self):
        if self.current_sound and self.sound_playing:
            self.current_sound.stop()
            self.sound_playing = False

    def start_timer(self, interval_seconds, alarm_callback):
        if self.is_running:
            return

        self.is_running = True

        def timer_thread():
            while self.is_running:
                time.sleep(interval_seconds)
                if self.is_running:
                    current_time = datetime.now().strftime("%H:%M:%S")
                    alarm_callback(f"ALARM! Time: {current_time}")
                    self.play_sound()

        self.current_timer = threading.Thread(target=timer_thread)
        self.current_timer.daemon = True
        self.current_timer.start()

    def stop_timer(self):
        self.is_running = False
        if self.current_timer and self.current_timer.is_alive():
            self.current_timer.join(timeout=1) # Give it a little time to stop

class TimerGUI:
    def __init__(self, master):
        self.master = master
        master.title("Custom Timer")

        self.timer = CustomTimer()

        self.interval_label = ttk.Label(master, text="Interval (minutes):")
        self.interval_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.interval_entry = ttk.Entry(master)
        self.interval_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.start_button = ttk.Button(master, text="Start Timer", command=self.start_timer)
        self.start_button.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

        self.stop_button = ttk.Button(master, text="Stop Timer", command=self.stop_timer, state=tk.DISABLED)
        self.stop_button.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

        self.set_sound_button = ttk.Button(master, text="Set Custom Sound", command=self.set_custom_sound)
        self.set_sound_button.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

        self.reset_sound_button = ttk.Button(master, text="Reset to Default Sound", command=self.reset_default_sound)
        self.reset_sound_button.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

        self.stop_current_sound_button = ttk.Button(master, text="Stop Current Sound", command=self.stop_current_sound)
        self.stop_current_sound_button.grid(row=5, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

        self.status_label = ttk.Label(master, text="Ready")
        self.status_label.grid(row=6, column=0, columnspan=2, padx=5, pady=5, sticky="w")

        master.grid_columnconfigure(1, weight=1) # Make the entry field expand

        self.os_platform = platform.system()
        if self.os_platform == "Windows":
            try:
                from win10toast import ToastNotifier
                self.toaster = ToastNotifier()
                self.has_windows_toaster = True
            except ImportError:
                print("Warning: win10toast not installed. Windows notifications will not be shown.")
                self.toaster = None
                self.has_windows_toaster = False
        elif self.os_platform == "Darwin":  # Darwin is the kernel for macOS
            pass # We'll handle macOS notifications in the update_status method
        else:
            print(f"Operating system '{self.os_platform}' not specifically supported for notifications.")

    def show_mac_notification(self, title, message):
        script = f'display notification "{message}" with title "{title}" sound name "default"'
        subprocess.run(['osascript', '-e', script])

    def start_timer(self):
        try:
            interval_minutes = float(self.interval_entry.get())
            if interval_minutes > 0:
                self.timer.start_timer(interval_minutes * 60, self.update_status)
                self.status_label.config(text=f"Timer started for {interval_minutes} minutes")
                self.start_button.config(state=tk.DISABLED)
                self.stop_button.config(state=tk.NORMAL)
            else:
                messagebox.showerror("Error", "Please enter a positive interval.")
        except ValueError:
            messagebox.showerror("Error", "Invalid interval. Please enter a number.")

    def stop_timer(self):
        self.timer.stop_timer()
        self.status_label.config(text="Timer stopped.")
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    def set_custom_sound(self):
        file_path = filedialog.askopenfilename(
            title="Select Custom Sound File",
            filetypes=(("Sound files", "*.wav *.mp3"), ("All files", "*.*"))
        )
        if file_path:
            if self.timer.set_sound(file_path):
                self.status_label.config(text=f"Custom sound set to: {os.path.basename(file_path)}")
            else:
                messagebox.showerror("Error", "Could not load the selected sound file.")
                self.status_label.config(text="Using default sound.")

    def reset_default_sound(self):
        self.timer.use_custom_sound = False
        self.status_label.config(text="Reset to default sound.")

    def stop_current_sound(self):
        self.timer.stop_current_sound()
        self.status_label.config(text="Current sound stopped (timer running).")

    def update_status(self, message):
        self.status_label.config(text=message)
        if self.os_platform == "Windows" and self.has_windows_toaster:
            self.toaster.show_toast(
                "Timer Alert!",
                message,
                duration=10,
                icon_path=None,
                threaded=True
            )
        elif self.os_platform == "Darwin":
            self.show_mac_notification("Alarm triggered: ", message)
        else:
            print(f"Alarm triggered: {message}") # Fallback for other OS

def main():
    root = tk.Tk()
    gui = TimerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()