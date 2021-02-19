import unittest
import tempfile

from pathlib import Path
from typing import List


from snapfs import file, transform, differences
from snapfs.datatypes import (
    File,
    Differences,
    Difference,
    FileAddedDifference,
    FileRemovedDifference,
    FileUpdatedDifference,
)


class TestDifferencesModule(unittest.TestCase):
    def test_serialize_difference_as_message(self):
        differences_instance = Differences(
            [
                FileAddedDifference(File(Path("foo.txt"))),
                FileUpdatedDifference(File(Path("bar.txt"))),
                FileRemovedDifference(File(Path("foobar.txt"))),
            ]
        )

        expected_result = [
            "added: foo.txt",
            "updated: bar.txt",
            "removed: foobar.txt",
        ]

        result = [
            differences.serialize_difference_as_message(x)
            for x in differences_instance.differences
        ]

        self.assertListEqual(result, expected_result)

    def test_serialize_differences_as_dict(self):
        file_added_instance = File(Path("foo.txt"))
        file_updated_instance = File(Path("bar.txt"))
        file_removed_instance = File(Path("foobar.txt"))

        differences_instance = Differences(
            [
                FileAddedDifference(file_added_instance),
                FileUpdatedDifference(file_updated_instance),
                FileRemovedDifference(file_removed_instance),
            ]
        )

        expected_result = {
            "differences": [
                {
                    "type": "FileAddedDifference",
                    "file": file.serialize_file_as_dict(file_added_instance),
                },
                {
                    "type": "FileUpdatedDifference",
                    "file": file.serialize_file_as_dict(file_updated_instance),
                },
                {
                    "type": "FileRemovedDifference",
                    "file": file.serialize_file_as_dict(file_removed_instance),
                },
            ]
        }

        result = differences.serialize_differences_as_dict(
            differences_instance
        )

        self.assertDictEqual(result, expected_result)
