import unittest
from unittest.mock import Mock
from wiki.web.converter import Converter, get_file_size # run with python -m unittest Tests/wiki_download_test/download_by_filetypes_test.py


class TestConverter(unittest.TestCase):
    def setUp(self):
        self.page = Mock()
        self.page.title = "Test Page"
        self.page.content = "Test content"

    def test_get_file_size(self):
        # Test get_file_size function with various sizes
        self.assertEqual(get_file_size(b''), '0 B')
        self.assertEqual(get_file_size(b'123'), '3 B')
        self.assertEqual(get_file_size(b'12345'), '5 B')
        self.assertEqual(get_file_size(b'1234567890'), '10 B')
        self.assertEqual(get_file_size(b'1' * 1024 * 1024), '1.00 MB')
        self.assertEqual(get_file_size(b'1' * 1024 * 1024 * 1024), '1.00 GB')

    def test_convert_to_PDF(self):
        converter = Converter(self.page)
        pdf_base64, file_size = converter.convert_to_PDF()

        self.assertTrue(isinstance(pdf_base64, str))
        self.assertTrue(isinstance(file_size, str))
        self.assertTrue(file_size.endswith('B'))

    def test_convert_to_TXT(self):
        converter = Converter(self.page)
        txt_base64, file_size = converter.convert_to_TXT()

        self.assertTrue(isinstance(txt_base64, str))
        self.assertTrue(isinstance(file_size, str))
        self.assertTrue(file_size.endswith('B'))

    def test_convert_to_HTML(self):
        converter = Converter(self.page)
        html_base64, file_size = converter.convert_to_HTML()

        self.assertTrue(isinstance(html_base64, str))
        self.assertTrue(isinstance(file_size, str))
        self.assertTrue(file_size.endswith('B'))

    def test_convert_to_DOCX(self):
        converter = Converter(self.page)
        docx_base64, file_size = converter.convert_to_DOCX()

        self.assertTrue(isinstance(docx_base64, str))
        self.assertTrue(isinstance(file_size, str))
        self.assertTrue(file_size.endswith('KB'))


if __name__ == '__main__':
    unittest.main()
