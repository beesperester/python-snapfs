import unittest
import tempfile
import json

from pathlib import Path
from typing import List


from snapfs import fs, transform, differences
from snapfs.datatypes import Differences, File


def get_named_tmpfile_path():
    tmpfile = tempfile.NamedTemporaryFile(mode="wb", delete=False)
    # tmpfile.write(file_contents)
    tmpfile.close()

    return Path(tmpfile.name)


class TestDifferencesModule(unittest.TestCase):
    def test_store_as_file(self):
        file_path = get_named_tmpfile_path()

        result = {}
        expected_result = {
            "added_files": [],
            "updated_files": [],
            "removed_files": [],
        }

        differences_instance = Differences()

        differences.store_as_file(file_path, differences_instance)

        with open(file_path, "r") as f:
            result = json.load(f)

        self.assertDictEqual(result, expected_result)

    def test_serialize_as_dict(self):
        expected_result = {
            "added_files": [],
            "updated_files": [],
            "removed_files": [],
        }

        differences_instance = Differences()

        result = differences.serialize_as_dict(differences_instance)

        self.assertDictEqual(result, expected_result)

    def test_deserialize_from_dict(self):
        expected_result = {
            "added_files": [],
            "updated_files": [],
            "removed_files": [],
        }

        result = differences.serialize_as_dict(
            differences.deserialize_from_dict(expected_result)
        )

        self.assertDictEqual(result, expected_result)

    def test_load_from_file(self):
        file_path = get_named_tmpfile_path()

        expected_result = {
            "added_files": [],
            "updated_files": [],
            "removed_files": [],
        }

        differences_instance = Differences()

        differences.store_as_file(file_path, differences_instance)

        result = differences.serialize_as_dict(
            differences.load_from_file(file_path)
        )

        self.assertDictEqual(result, expected_result)
