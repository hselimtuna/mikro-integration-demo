import logging
import queue
from threading import Lock

class GUILogHandler(logging.Handler):

    def __init__(self):
        super().__init__()
        self.log_queue = queue.Queue()
        self._lock = Lock()

    def emit(self, record):

        with self._lock:
            try:

                formatted_message = self.format(record)
                log_entry = {
                    'level': record.levelname,
                    'timestamp': record.created,
                    'message': record.getMessage(),
                    'formatted': formatted_message
                }
                self.log_queue.put(log_entry)
            except Exception:
                self.handleError(record)

    def get_log_entry(self):

        try:
            return self.log_queue.get_nowait()
        except queue.Empty:
            return None

    def clear_queue(self):

        with self._lock:
            while not self.log_queue.empty():
                try:
                    self.log_queue.get_nowait()
                except queue.Empty:
                    break