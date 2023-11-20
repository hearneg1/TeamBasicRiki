import os
import shutil
import sys
import unittest

sys.path.append(os.path.join(os.getcwd(), "wiki")) # used to make test run, still need to run from command line
from wiki.web.file_storage import FileManager # run with python -m unittest Tests/file_storage_test.py


class TestFileStorage(unittest.TestCase):
    def setUp(self):
        self.directory = os.path.join("Tests", "test_directory")
        if not os.path.exists(self.directory):
            os.mkdir(self.directory)
        for file in os.listdir(self.directory):
            os.remove(os.path.join(self.directory, file))
        self.file_manager = FileManager(self.directory)

    def test_get_downloadable_files(self):
        files = self.file_manager.get_downloadable_files()
        self.assertEqual(files, [])
        open(os.path.join(self.directory, "test_text.txt"), "w").close()
        files = self.file_manager.get_downloadable_files()
        self.assertEqual(files[0], "test_text.txt")


if __name__ == '__main__':
    unittest.main()
