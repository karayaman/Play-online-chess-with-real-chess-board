from threading import Thread
from queue import Queue
import pyttsx3


class Speech_thread(Thread):

    def __init__(self, *args, **kwargs):
        super(Speech_thread, self).__init__(*args, **kwargs)
        self.queue = Queue()

    def run(self):
        while True:
            engine = pyttsx3.init()
            text = self.queue.get()
            engine.say(text)
            engine.runAndWait()

    def put_text(self, text):
        self.queue.put(text)
