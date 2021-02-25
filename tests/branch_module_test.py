import unittest
import tempfile
import json

from pathlib import Path
from typing import List


from snapfs import fs, transform, branch
from snapfs.datatypes import Branch, Tag


def get_named_tmpfile_path():
    tmpfile = tempfile.NamedTemporaryFile(mode="wb", delete=False)
    # tmpfile.write(file_contents)
    tmpfile.close()

    return Path(tmpfile.name)


class TestBranchModule(unittest.TestCase):
    def test_store_branch_as_file(self):
        file_path = get_named_tmpfile_path()

        branch_instance = Branch()

        data = {"commit_hashid": ""}

        result = ""
        expected_result = transform.dict_as_json(data)

        branch.store_as_file(file_path, branch_instance)

        with open(file_path, "r") as f:
            result = f.read()

        self.assertEqual(result, expected_result)

    def test_load_file_as_branch(self):
        file_path = get_named_tmpfile_path()

        branch_instance = Branch()

        result = {}
        expected_result = branch.serialize_as_dict(branch_instance)

        branch.store_as_file(file_path, branch_instance)

        result = branch.serialize_as_dict(
            branch.load_from_file(file_path)
        )

        self.assertDictEqual(result, expected_result)

    def test_serialize_branch_as_dict(self):
        data = {"commit_hashid": ""}

        branch_instance = Branch()

        expected_result = data
        result = branch.serialize_as_dict(branch_instance)

        self.assertDictEqual(result, expected_result)

    def test_deserialize_dict_as_branch(self):
        data = {"commit_hashid": ""}

        expected_result = data
        result = branch.serialize_as_dict(
            branch.deserialize_from_dict(data)
        )

        self.assertDictEqual(result, expected_result)
