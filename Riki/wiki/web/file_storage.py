import os


class DownloadFiles(object):
    def __init__(self, directory):
        self._directory = directory

    def get_downloadable_files(self):
        return os.listdir(self._directory)


class UploadFiles(object):
    def __init__(self, directory):
        self._directory = directory
