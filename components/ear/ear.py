import os 
import speech_recognition as sr
from concurrent import futures
import sys
import numpy as np 
import warnings

# Redirect stderr to /dev/null
devnull = os.open(os.devnull, os.O_WRONLY)
old_stderr = os.dup(2)
sys.stderr.flush()
os.dup2(devnull, 2)
os.close(devnull)

API_KEY = os.getenv("OPENAI_API_KEY")

class Ear:
    def __init__(self):
        self.rec = sr.Recognizer()
        self.mic = sr.Microphone()

        self.pool = futures.ThreadPoolExecutor(max_workers=1, thread_name_prefix="Rec Thread")
        self.speech = []

    def grab_audio(self) -> sr.AudioData:
        print("Listening...")
        with self.mic as source:
            audio = self.rec.listen(source, phrase_time_limit=2)

        return audio

    def is_speech(self, audio_data: sr.AudioData, threshold=0.01):
        data = np.frombuffer(audio_data.frame_data, dtype=np.int16) #converting from audio data(bytes) to np array
        energy = np.sum(data.astype(float)**2)/len(data)
        return energy > threshold

    def recognize_audio_thread_pool(self, audio_data: sr.AudioData):
        future = self.pool.submit(self.get_text, audio_data)
        future.add_done_callback(self.post_process_callback)

    def post_process_callback(self, future):
        result = future.result()
        print(f"Recognized: {result}")

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
