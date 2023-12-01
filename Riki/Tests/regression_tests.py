"""
This is the regression testing file. Use this file in order to run all of the unit tests at once. This saves
the time of running each individually

"""


import unittest
import os
import sys
project_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_path)


def run_tests():
    test_suite = unittest.TestSuite()
    test_suite.addTests(unittest.TestLoader().discover('Tests/account_test', pattern='*_test.py'))
    test_suite.addTests(unittest.TestLoader().discover('Tests/file_storage_test', pattern='*_test.py'))
    test_suite.addTests(unittest.TestLoader().discover('Tests/wiki_download_test', pattern='*_test.py'))
    run_test_suite = unittest.TextTestRunner()
    run_test_suite.run(test_suite)


if __name__ == "__main__":
    run_tests()
