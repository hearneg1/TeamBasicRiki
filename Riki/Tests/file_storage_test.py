import io
import os
import sys
import unittest
from unittest import mock
from unittest.mock import patch
from werkzeug.datastructures import FileStorage

sys.path.append(os.path.join(os.getcwd(), "wiki"))  # used to make test run, still need to run from command line
from wiki.web.file_storage import FileManager  # run with python -m unittest Tests/file_storage_test.py


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

    def test_download_file(self):
        pass  # no idea how to unit test send_from_directory call inside this function

    def test_upload_file_success(self):
        test_file_name = "test_upload.txt"
        file = FileStorage(  # Used to copy how flask's upload file structure creates a file
            filename=test_file_name,
            content_type="text/plain"
        )
        result = self.file_manager.upload_file(file)
        self.assertTrue(result)

    def test_upload_file_failure_empty_name(self):
        test_file_name = ""
        file = FileStorage(  # Used to copy how flask's upload file structure creates a file
            filename=test_file_name,
            content_type="text/plain"
        )
        result = self.file_manager.upload_file(file)
        self.assertFalse(result)

    def test_upload_file_failure_duplicate_name(self):
        test_file_name = "test_upload.txt"
        open(os.path.join(self.directory, test_file_name), "w").close()  # create duplicate
        file = FileStorage(  # Used to copy how flask's upload file structure creates a file
            filename=test_file_name,
            content_type="text/plain"
        )
        result = self.file_manager.upload_file(file)
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
