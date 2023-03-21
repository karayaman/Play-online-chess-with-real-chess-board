from threading import Thread
from queue import Queue


class VideoCaptureThread(Thread):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queue = Queue()
        self.capture = None

    def run(self):
        while True:
            ret, frame = self.capture.read()
            if ret is False:
                continue
            self.queue.put(frame)

    def get_frame(self):
        return self.queue.get()
