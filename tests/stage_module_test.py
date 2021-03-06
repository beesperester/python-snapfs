import unittest
import tempfile
import json

from pathlib import Path
from typing import List


from snapfs import fs, transform, stage
from snapfs.datatypes import Stage, File


def get_named_tmpfile_path():
    tmpfile = tempfile.NamedTemporaryFile(mode="wb", delete=False)
    # tmpfile.write(file_contents)
    tmpfile.close()

    return Path(tmpfile.name)


class TestStageModule(unittest.TestCase):
    def test_store_as_file(self):
        file_path = get_named_tmpfile_path()

        result = {}
        expected_result = {
            "added_files": [],
            "updated_files": [],
            "removed_files": [],
        }

        stage_instance = Stage()

        stage.store_as_file(file_path, stage_instance)

        with open(file_path, "r") as f:
            result = json.load(f)

        self.assertDictEqual(result, expected_result)

    def test_serialize_as_dict(self):
        expected_result = {
            "added_files": [],
            "updated_files": [],
            "removed_files": [],
        }

        stage_instance = Stage()

        result = stage.serialize_as_dict(stage_instance)

        self.assertDictEqual(result, expected_result)

    def test_deserialize_from_dict(self):
        expected_result = {
            "added_files": [],
            "updated_files": [],
            "removed_files": [],
        }

        result = stage.serialize_as_dict(
            stage.deserialize_from_dict(expected_result)
        )

        self.assertDictEqual(result, expected_result)

    def test_load_from_file(self):
        file_path = get_named_tmpfile_path()

        expected_result = {
            "added_files": [],
            "updated_files": [],
            "removed_files": [],
        }

        stage_instance = Stage()

        stage.store_as_file(file_path, stage_instance)

        result = stage.serialize_as_dict(stage.load_from_file(file_path))

        self.assertDictEqual(result, expected_result)
