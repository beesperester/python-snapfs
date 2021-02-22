import unittest
import tempfile
import json

from pathlib import Path
from typing import List


from snapfs import fs, transform, tag
from snapfs.datatypes import Tag


def get_named_tmpfile_path():
    tmpfile = tempfile.NamedTemporaryFile(mode="wb", delete=False)
    # tmpfile.write(file_contents)
    tmpfile.close()

    return Path(tmpfile.name)


class TestTagModule(unittest.TestCase):
    def test_store_tag_as_file(self):
        file_path = get_named_tmpfile_path()

        tag_instance = Tag("1.0.0")

        data = {"tag": "1.0.0", "message": "", "commit_hashid": ""}

        result = ""
        expected_result = transform.dict_as_json(data)

        tag.store_tag_as_file(file_path, tag_instance)

        with open(file_path, "r") as f:
            result = f.read()

        self.assertEqual(result, expected_result)

    def test_load_file_as_tag(self):
        file_path = get_named_tmpfile_path()

        tag_instance = Tag("1.0.0")

        result = {}
        expected_result = tag.serialize_tag_as_dict(tag_instance)

        tag.store_tag_as_file(file_path, tag_instance)

        result = tag.serialize_tag_as_dict(tag.load_file_as_tag(file_path))

        self.assertDictEqual(result, expected_result)

    def test_serialize_tag_as_dict(self):
        data = {"tag": "1.0.0", "message": "", "commit_hashid": ""}

        tag_instance = Tag("1.0.0")

        expected_result = data
        result = tag.serialize_tag_as_dict(tag_instance)

        self.assertDictEqual(result, expected_result)

    def test_deserialize_dict_as_tag(self):
        data = {"tag": "1.0.0", "message": "", "commit_hashid": ""}

        expected_result = data
        result = tag.serialize_tag_as_dict(tag.deserialize_dict_as_tag(data))

        self.assertDictEqual(result, expected_result)
