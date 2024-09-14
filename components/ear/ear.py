import os 
import speech_recognition as sr
from concurrent import futures
import sys
import numpy as np 
import warnings
import requests
import time
import serial


warnings.filterwarnings("ignore")

# Redirect stderr to /dev/null
devnull = os.open(os.devnull, os.O_WRONLY)
old_stderr = os.dup(2)
sys.stderr.flush()
os.dup2(devnull, 2)
os.close(devnull)

API_KEY = os.getenv("OPENAI_API_KEY")
legs = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
legs.flush()

class Ear:
    def __init__(self, process_internal=20):
        self.rec = sr.Recognizer()
        self.mic = sr.Microphone()

        self.pool = futures.ThreadPoolExecutor(max_workers=1, thread_name_prefix="Rec Thread")
        self.speech = []
        self.last_process_time = 0
        self.process_interval = process_internal  # 20 seconds interval

    def grab_audio(self) -> sr.AudioData:
        print("Listening...")
        with self.mic as source:
            audio = self.rec.listen(source, phrase_time_limit=2)
        return audio

    def is_speech(self, audio_data: sr.AudioData, threshold=0.5):
        data = np.frombuffer(audio_data.frame_data, dtype=np.int16)
        energy = np.sum(data.astype(float)**2)/len(data)
        return energy > threshold

    def recognize_audio_thread_pool(self, audio_data: sr.AudioData):
        current_time = time.time()
        if current_time - self.last_process_time >= self.process_interval:
            self.last_process_time = current_time
            future = self.pool.submit(self.get_text, audio_data)
            future.add_done_callback(self.post_process_callback)
        else:
            print(f"Skipping processing. {self.process_interval - (current_time - self.last_process_time):.1f} seconds until next process.")

    def post_process_callback(self, future):
        result = future.result().lower()
        print(f"***********Recognized: {result}")

        if "forward" in result:
            self.send_command("U")
        elif "backward" in result:
            self.send_command("D")
        elif "left" in result:
            self.send_command("L")
        elif "right" in result:
            self.send_command("R")


        # self.get_command(result)

    def send_command(self, command: str):
        if command in ['U', 'D', 'L', 'R']:
            legs.write(command.encode())
        else:
            print("Invalid command. Please use 'U', 'D', 'L', 'R'")


    def get_command(self, command: str):
        url = "http://localhost:5002/vector/voice_command"
        payload = {"voice_message": command}
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            print(response.json())
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")

    def get_text(self, audio: sr.AudioData) -> str:
        print("Waiting for text from whisper-1...")
        try:
            text = self.rec.recognize_whisper_api(audio, model="whisper-1", api_key=API_KEY)
        except sr.UnknownValueError:
            text = "ERROR: Failed to recognize speech"
        except sr.RequestError as e:
            text = f"ERROR: Invalid request:{e}"
        return text #future.result()

    def listen(self):
        print("Adjusting for ambient noise...")
        with self.mic as source:
            self.rec.adjust_for_ambient_noise(source, duration=5)

        try:
            while True:
                audio = self.grab_audio()
                if self.is_speech(audio):
                    print("Speech detected, processing...")
                    self.recognize_audio_thread_pool(audio)
                else:
                    print("No speech detected, continuing to listen")
        except KeyboardInterrupt:
            print("Finishing up...")
        finally:
            self.pool.shutdown(wait=True)

            #restore stderr
            os.dup2(old_stderr, 2)
            os.close(old_stderr)
