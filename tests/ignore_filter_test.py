import unittest

from typing import List


from snapfs.filters import ignore


exclude_all_include_some = ["*", "^*.c4d", "^*.png"]

include_all_exclude_some = ["*.txt", "filename.png"]


class TestIgnoreFilters(unittest.TestCase):
    def test_exclude_all_include_some_c4d(self):
        self.assertEqual(
            ignore("filename.c4d", exclude_all_include_some), False
        )

    def test_exclude_all_include_some_txt(self):
        self.assertEqual(
            ignore("filename.txt", exclude_all_include_some), True
        )

    def test_exclude_all_include_some_png(self):
        self.assertEqual(
            ignore("filename.png", exclude_all_include_some), False
        )

    def test_include_all_exclude_some_c4d(self):
        self.assertEqual(
            ignore("filename.c4d", include_all_exclude_some), False
        )

    def test_include_all_exclude_some_txt(self):
        self.assertEqual(
            ignore("filename.txt", include_all_exclude_some), True
        )

    def test_include_all_exclude_some_png(self):
        self.assertEqual(
            ignore("filename.png", include_all_exclude_some), True
        )
