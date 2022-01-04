from threading import Thread
from queue import Queue
import platform


class SpeechThread(Thread):

    def __init__(self, *args, **kwargs):
        super(SpeechThread, self).__init__(*args, **kwargs)
        self.queue = Queue()
        self.index = None

    def run(self):
        if platform.system() == "Darwin":
            import mac_say
            name = mac_say.voices()[self.index][0]
            while True:
                text = self.queue.get()
                mac_say.say([text, "-v", name])
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
