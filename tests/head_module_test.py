import unittest
import tempfile
import json

from pathlib import Path
from typing import List


from snapfs import fs, transform, head
from snapfs.datatypes import Head


def get_named_tmpfile_path():
    tmpfile = tempfile.NamedTemporaryFile(mode="wb", delete=False)
    # tmpfile.write(file_contents)
    tmpfile.close()

    return Path(tmpfile.name)


class TestHeadModule(unittest.TestCase):
    def test_store_head_as_file(self):
        file_path = get_named_tmpfile_path()

        data = {"ref": ""}

        result = ""
        expected_result = transform.dict_as_json(data)

        head_instance = Head()

        head.store_head_as_file(file_path, head_instance)

        with open(file_path, "r") as f:
            result = f.read()

        self.assertEqual(result, expected_result)

    def test_load_file_as_head(self):
        file_path = get_named_tmpfile_path()

        head_instance = Head()

        head.store_head_as_file(file_path, head_instance)

        expected_result = head.serialize_head_as_dict(head_instance)
        result = head.serialize_head_as_dict(head.load_file_as_head(file_path))

        self.assertEqual(result, expected_result)

    def test_serialize_head_as_dict(self):
        expected_result = {"ref": ""}

        head_instance = Head()

        result = head.serialize_head_as_dict(head_instance)

        self.assertDictEqual(result, expected_result)
