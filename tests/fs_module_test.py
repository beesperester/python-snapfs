import unittest
import tempfile
import json

from pathlib import Path
from typing import List


from snapfs import fs, transform


def get_named_tmpfile_path():
    tmpfile = tempfile.NamedTemporaryFile(mode="wb", delete=False)
    # tmpfile.write(file_contents)
    tmpfile.close()

    return Path(tmpfile.name)


class TestFSModule(unittest.TestCase):
    def test_make_dirs(self):
        directory_exists = False

        with tempfile.TemporaryDirectory() as tmpdirname:
            directory_path = Path(tmpdirname).joinpath("foobar")

            fs.make_dirs(directory_path)

            directory_exists = directory_path.is_dir()

        self.assertTrue(directory_exists)

    def test_save_file(self):
        file_path = get_named_tmpfile_path()

        fs.save_file(file_path, "hello world", override=True)

        result = ""
        expected_result = "hello world"

        with open(file_path, "r") as f:
            result = f.read()

        self.assertEqual(result, expected_result)

    def test_save_data_as_file(self):
        file_path = get_named_tmpfile_path()

        result = {}
        expected_result = {"hello": "world"}

        fs.save_dict_as_file(file_path, expected_result, override=True)

        with open(file_path, "r") as f:
            result = json.load(f)

        self.assertDictEqual(result, expected_result)

    def test_save_data_as_blob(self):
        data = {"hello": "world"}

        result = ""
        expected_result = transform.string_to_hashid(
            transform.dict_to_json(data)
        )
        with tempfile.TemporaryDirectory() as tmpdirname:
            result = fs.save_dict_as_blob(Path(tmpdirname), data)

        self.assertEqual(result, expected_result)

    def test_load_file(self):
        data = "foobar"

        expected_result = data

        file_path = get_named_tmpfile_path()

        with open(file_path, "w") as f:
            f.write(data)

        result = fs.load_file(file_path)

        self.assertEqual(result, expected_result)

    def test_load_file_as_data(self):
        data = {"hello": "world"}

        expected_result = data

        file_path = get_named_tmpfile_path()

        with open(file_path, "w") as f:
            f.write(transform.dict_to_json(data))

        result = fs.load_file_as_dict(file_path)

        self.assertDictEqual(result, expected_result)

    def test_load_blob_as_dict(self):
        data = {"hello": "world"}

        result = {}
        expected_result = data

        file_path = get_named_tmpfile_path()

        with tempfile.TemporaryDirectory() as tmpdirname:
            hashid = fs.save_dict_as_blob(Path(tmpdirname), data)

            result = fs.load_blob_as_dict(Path(tmpdirname), hashid)

        self.assertDictEqual(result, expected_result)

    def test_copy_file(self):
        source_file_path = get_named_tmpfile_path()
        target_file_path = source_file_path.parent.joinpath("foobar")

        fs.copy_file(source_file_path, target_file_path)

        self.assertTrue(target_file_path.is_file())

    def test_copy_file_as_blob(self):
        data = b"hello world"

        expected_result = transform.bytes_to_hashid(data)

        source_file_path = get_named_tmpfile_path()

        with open(source_file_path, "wb") as f:
            f.write(data)

        with tempfile.TemporaryDirectory() as tmpdirname:
            result = fs.copy_file_as_blob(Path(tmpdirname), source_file_path)

        self.assertEqual(result, expected_result)

    def test_load_ignore_file(self):
        result = []
        expected_result = ["*", "^*.c4d"]

        data = "\n".join(expected_result)

        with tempfile.TemporaryDirectory() as tmpdirname:
            ignore_file_path = Path(tmpdirname).joinpath(".ignore")

            with open(ignore_file_path, "w") as f:
                f.write(data)

            result = fs.load_ignore_file(Path(tmpdirname))

        self.assertListEqual(result, expected_result)
