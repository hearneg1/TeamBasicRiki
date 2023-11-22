import os
from flask import send_from_directory

class FileManager(object):
    def __init__(self, directory):
        self._directory = directory
        if not os.path.exists(self._directory):
            os.mkdir(self._directory)

    def get_downloadable_files(self):
        return os.listdir(self._directory)

    def download_file(self, file_name):
       dir_path = os.path.join(os.getcwd(), self._directory)
       return send_from_directory(dir_path, file_name, as_attachment=True)

    def upload_file(self, file):
        current_files = self.get_downloadable_files()
        if file.filename == "" or file.filename in current_files:
            return False
        file.save(os.path.join(self._directory, file.filename))
        return True

    def delete_file(self, file_name):
        current_files = self.get_downloadable_files()
        if file_name not in current_files:
            return False
        os.remove(os.path.join(self._directory, file_name))
        return True

