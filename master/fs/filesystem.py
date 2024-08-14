import os
import uuid
import threading

from config import Config


class Handler:
    def __init__(self):
        self.upload_folder = Config.UPLOAD_FOLDER
        self.__lock = threading.Lock()

        if not os.path.exists(self.upload_folder):
            os.makedirs(self.upload_folder)

    def create_file(self, file):
        if not file:
            raise ValueError("No file provided")

        file_extension = file.filename.rsplit('.', 1)[1].lower()
        filename = str(uuid.uuid4())

        with self.__lock:
            file.save(os.path.join(self.upload_folder, filename))

        return filename

    def get_handle(self, filename):
        filepath = os.path.join(self.upload_folder, filename)
        handle = open(filepath, "rb")

        return handle
