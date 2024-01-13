import cv2
import numpy as np
import pyautogui
import sounddevice as sd
import soundfile as sf
import threading
import tkinter as tk
from tkinter import filedialog

class ScreenRecorderApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Screen Recorder")

        self.recording = False
        self.audio_thread = None
        self.video_thread = None
        self.audio_filename = "audio.wav"
        self.video_filename = "screen_record.avi"

        # GUI элементы
        self.start_button = tk.Button(master, text="Start Recording", command=self.start_recording)
        self.start_button.pack(pady=10)

        self.stop_button = tk.Button(master, text="Stop Recording", command=self.stop_recording, state=tk.DISABLED)
        self.stop_button.pack(pady=10)

        self.save_button = tk.Button(master, text="Save Recording", command=self.save_recording, state=tk.DISABLED)
        self.save_button.pack(pady=10)

    def start_recording(self):
        self.recording = True
        self.audio_thread = threading.Thread(target=self.record_audio)
        self.audio_thread.start()
        self.video_thread = threading.Thread(target=self.record_screen)
        self.video_thread.start()

        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.save_button.config(state=tk.DISABLED)

    def stop_recording(self):
        self.recording = False

        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.save_button.config(state=tk.NORMAL)

    def save_recording(self):
        filename = filedialog.asksaveasfilename(defaultextension=".avi", filetypes=[("AVI files", "*.avi")])
        if filename:
            video_data = cv2.VideoCapture(self.video_filename)
            audio_data, _ = sf.read(self.audio_filename, dtype='float32')

            fourcc = cv2.VideoWriter_fourcc(*"XVID")
            out = cv2.VideoWriter(filename, fourcc, 20.0, (int(video_data.get(3)), int(video_data.get(4))))

            while True:
                ret, frame = video_data.read()
                if not ret:
                    break
                out.write(frame)

            out.release()
            video_data.release()

    def record_audio(self):
        channels = 2
        samplerate = 44100

        with sf.SoundFile(self.audio_filename, mode='x', samplerate=samplerate, channels=channels) as file:
            with sd.InputStream(callback=lambda indata, frames, time, status: file.write(indata)):
                sd.sleep(1000000)

    def record_screen(self):
        screensize = pyautogui.size()
        fourcc = cv2.VideoWriter_fourcc(*"XVID")
        out = cv2.VideoWriter(self.video_filename, fourcc, 20.0, (screensize.width, screensize.height))

        while self.recording:
            img = pyautogui.screenshot()
            frame = np.array(img)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            out.write(frame)

        out.release()

# Создание и запуск приложения
root = tk.Tk()
app = ScreenRecorderApp(root)
root.mainloop()
