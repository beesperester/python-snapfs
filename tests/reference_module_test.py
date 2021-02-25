import unittest
import tempfile
import json

from pathlib import Path
from typing import List


from snapfs import fs, transform, reference
from snapfs.datatypes import Reference


def get_named_tmpfile_path():
    tmpfile = tempfile.NamedTemporaryFile(mode="wb", delete=False)
    # tmpfile.write(file_contents)
    tmpfile.close()

    return Path(tmpfile.name)


class TestReferenceModule(unittest.TestCase):
    def test_serialize_reference_as_dict(self):
        data = {"commit_hashid": ""}

        reference_instance = Reference()

        expected_result = data
        result = reference.serialize_as_dict(reference_instance)

        self.assertDictEqual(result, expected_result)
