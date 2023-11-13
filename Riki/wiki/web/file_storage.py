import os


class FileManager(object):
    def __init__(self, directory):
        self._directory = directory

    def get_downloadable_files(self):
        return os.listdir(self._directory)

