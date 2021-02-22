from os import makedirs
import unittest
import tempfile
import json

from pathlib import Path
from typing import List


from snapfs import fs, transform, branch, repository, head
from snapfs.datatypes import Branch, Tag, Head


def get_named_tmpfile_path():
    tmpfile = tempfile.NamedTemporaryFile(mode="wb", delete=False)
    # tmpfile.write(file_contents)
    tmpfile.close()

    return Path(tmpfile.name)


class TestRepositoryModule(unittest.TestCase):
    def test_get_repository_path(self):
        expected_result = "foobar/.snapfs"

        result = str(repository.get_repository_path(Path("foobar"), False))

        self.assertEqual(result, expected_result)

    def test_get_blobs_path(self):
        expected_result = "foobar/.snapfs/blobs"

        result = str(repository.get_blobs_path(Path("foobar"), False))

        self.assertEqual(result, expected_result)

    def test_get_references_path(self):
        expected_result = "foobar/.snapfs/references"

        result = str(repository.get_references_path(Path("foobar"), False))

        self.assertEqual(result, expected_result)

    def test_get_branches_path(self):
        expected_result = "foobar/.snapfs/references/branches"

        result = str(repository.get_branches_path(Path("foobar"), False))

        self.assertEqual(result, expected_result)

    def test_get_tags_path(self):
        expected_result = "foobar/.snapfs/references/tags"

        result = str(repository.get_tags_path(Path("foobar"), False))

        self.assertEqual(result, expected_result)

    def test_get_stage_path(self):
        expected_result = "foobar/.snapfs/stage"

        result = str(repository.get_stage_path(Path("foobar"), False))

        self.assertEqual(result, expected_result)

    def test_get_head_path(self):
        expected_result = "foobar/.snapfs/HEAD"

        result = str(repository.get_head_path(Path("foobar"), False))

        self.assertEqual(result, expected_result)

    def test_get_head(self):
        head_instance = Head()

        expected_result = head.serialize_head_as_dict(head_instance)

        result = {}
        with tempfile.TemporaryDirectory() as tmpdirname:
            tmppath = Path(tmpdirname)

            head_path = repository.get_head_path(tmppath, False)

            makedirs(head_path.parent, exist_ok=True)

            head.store_head_as_file(head_path, head_instance)

            result = head.serialize_head_as_dict(repository.get_head(tmppath))

        self.assertEqual(result, expected_result)
