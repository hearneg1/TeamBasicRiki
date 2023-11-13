import os


class FileManager(object):
    def __init__(self, directory):
        self._directory = directory

    def get_downloadable_files(self):
        return os.listdir(self._directory)

    def upload_file(self, file):
        current_files = self.get_downloadable_files()
        if file.filename in current_files:
            return False
        file.save(os.path.join(self._directory, file.filename))
        return True

