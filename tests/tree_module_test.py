import os
import unittest
import tempfile
import json

from pathlib import Path
from typing import List


from snapfs import fs, transform, stage, tree, file
from snapfs.datatypes import File, Directory


def get_named_tmpfile_path():
    tmpfile = tempfile.NamedTemporaryFile(mode="wb", delete=False)
    # tmpfile.write(file_contents)
    tmpfile.close()

    return Path(tmpfile.name)


class TestTreeModule(unittest.TestCase):
    def test_store_tree_as_blob(self):
        tree_instance = Directory()

        result = ""
        expected_result = transform.string_as_hashid(
            transform.dict_as_json(tree.serialize_tree_as_dict(tree_instance))
        )

        with tempfile.TemporaryDirectory() as tmpdirname:
            result = tree.store_tree_as_blob(Path(tmpdirname), tree_instance)

        self.assertEqual(result, expected_result)

    def test_load_blob_as_tree(self):
        tree_instance = Directory()

        result = {}
        expected_result = {"directories": {}, "files": {}}

        with tempfile.TemporaryDirectory() as tmpdirname:
            tree_hashid = tree.store_tree_as_blob(
                Path(tmpdirname), tree_instance
            )

            result = tree.serialize_tree_as_dict(
                tree.load_blob_as_tree(Path(tmpdirname), tree_hashid)
            )

        self.assertDictEqual(result, expected_result)

    def test_serialize_tree_as_hashid(self):
        tree_instance = Directory()

        data = {"directories": {}, "files": {}}

        expected_result = transform.dict_as_hashid(data)
        result = tree.serialize_tree_as_hashid(tree_instance)

        self.assertEqual(result, expected_result)

    def test_serialize_tree_as_dict(self):
        directories = {"test": Directory()}

        tree_instance = Directory(directories)

        expected_result = {
            "directories": {"test": {"directories": {}, "files": {}}},
            "files": {},
        }

        result = tree.serialize_tree_as_dict(tree_instance)

        self.assertDictEqual(result, expected_result)

    def test_tree_as_list(self):
        file_instance = File(Path("test"))

        directories = {}
        files = {"test": file_instance}

        tree_instance = Directory(directories, files)

        expected_result = [file.serialize_file_as_dict(file_instance)]
        result = [
            file.serialize_file_as_dict(x)
            for x in tree.tree_as_list(Path(), tree_instance)
        ]

        self.assertListEqual(result, expected_result)

    def test_list_as_tree(self):
        file_instance = File(Path("test/foobar"))

        data = [file_instance]

        expected_result = {
            "directories": {
                "test": {
                    "directories": {},
                    "files": {
                        "foobar": file.serialize_file_as_dict(file_instance)
                    },
                }
            },
            "files": {},
        }
        result = tree.serialize_tree_as_dict(tree.list_as_tree(Path(), data))

        self.assertEqual(result, expected_result)

    def test_load_directory_path_as_tree(self):
        tree_instance = Directory()
        fake_file_path = Path()

        with tempfile.TemporaryDirectory() as tmpdirname:
            ignore_file_path = Path(tmpdirname).joinpath(".ignore")

            # add ignore file
            with open(ignore_file_path, "w") as f:
                f.write("\n".join(["*", "^*.c4d"]))

            # create subdirectory "test"
            test_directory_path = Path(tmpdirname).joinpath("test")

            os.makedirs(test_directory_path)

            # create fake binary file
            fake_file_path = test_directory_path.joinpath("foo.c4d")

            with open(fake_file_path, "wb") as f:
                f.write(b"fake binary data")

            tree_instance = tree.load_directory_path_as_tree(Path(tmpdirname))

        expected_result = {
            "directories": {
                "test": {
                    "directories": {},
                    "files": {
                        "foo.c4d": file.serialize_file_as_dict(
                            File(fake_file_path)
                        )
                    },
                }
            },
            "files": {},
        }

        result = tree.serialize_tree_as_dict(tree_instance)

        self.assertDictEqual(result, expected_result)
