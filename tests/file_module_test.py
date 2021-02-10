import unittest
import tempfile

from pathlib import Path
from typing import List


from snapfs import file, transform
from snapfs.datatypes import File

file_contents = b"hello world"

tmpfile = tempfile.NamedTemporaryFile(mode="wb", delete=False)
tmpfile.write(file_contents)
tmpfile.close()

file_instance = File(Path(tmpfile.name))

expected_result = {
    "path": str(tmpfile.name),
    "is_blob": False,
    "blob_path": None,
    "hashid": "",
}


class TestCommitModule(unittest.TestCase):
    def test_file_datatype(self):

        self.assertDictEqual(
            file.serialize_file_as_dict(file_instance),
            expected_result,
        )

    def test_serialize_file_as_hashid(self):
        self.assertEqual(
            file.serialize_file_as_hashid(file_instance),
            transform.bytes_to_hashid(file_contents),
        )

    def test_serialize_file_as_dict(self):
        self.assertEqual(
            file.serialize_file_as_dict(file_instance), expected_result
        )

    def test_deserialize_dict_as_file(self):
        result = file.deserialize_dict_as_file(expected_result)

        self.assertEqual(file.serialize_file_as_dict(result), expected_result)

    def test_store_file_as_blob(self):
        file_hashid = ""

        with tempfile.TemporaryDirectory() as tmpdirname:
            file_hashid = file.store_file_as_blob(
                Path(tmpdirname), file_instance
            )

        self.assertEqual(
            file_hashid,
            transform.bytes_to_hashid(file_contents),
        )

    def test_load_blob_as_file(self):
        file_hashid = ""

        with tempfile.TemporaryDirectory() as tmpdirname:
            file_hashid = file.store_file_as_blob(
                Path(tmpdirname), file_instance
            )

            result_file_instance = file.load_blob_as_file(
                Path(tmpdirname), file_hashid
            )

        blob_path = Path(tmpdirname).joinpath(
            transform.hashid_to_path(file_hashid)
        )

        expected_result_file_instance = File(
            blob_path,
            True,
            blob_path,
            file_hashid,
        )

        self.assertEqual(
            file.serialize_file_as_dict(result_file_instance),
            file.serialize_file_as_dict(expected_result_file_instance),
        )
