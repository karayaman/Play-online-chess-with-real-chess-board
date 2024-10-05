from threading import Thread
from queue import Queue
import platform
import os
import subprocess


class Speech_thread(Thread):

    def __init__(self, *args, **kwargs):
        super(Speech_thread, self).__init__(*args, **kwargs)
        self.queue = Queue()
        self.index = None

    def run(self):
        if platform.system() == "Darwin":
            result = subprocess.run(['say', '-v', '?'], stdout=subprocess.PIPE)
            output = result.stdout.decode('utf-8')
            voices = []
            for line in output.splitlines():
                if line:
                    voices.append(line.split()[0])
            name = voices[self.index]
            while True:
                text = self.queue.get()
                os.system(f'say -v {name} "{text}"')
        else:
            import pyttsx3
            while True:
                engine = pyttsx3.init()
                voices = engine.getProperty('voices')
                voice = voices[self.index]
                engine.setProperty('voice', voice.id)
                text = self.queue.get()
                engine.say(text)
                engine.runAndWait()

    def put_text(self, text):
        self.queue.put(text)
