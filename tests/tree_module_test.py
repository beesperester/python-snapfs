import os
import unittest
import tempfile
import json
import random
import string

from pathlib import Path
from typing import List


from snapfs import fs, transform, stage, tree, file, differences
from snapfs.datatypes import File, Directory, Difference


def get_named_tmpfile_path() -> Path:
    tmpfile = tempfile.NamedTemporaryFile(mode="wb", delete=False)
    # tmpfile.write(file_contents)
    tmpfile.close()

    return Path(tmpfile.name)


def fill_tmpfile(path: Path) -> None:
    with open(path, "w") as f:
        f.write(
            "".join(random.choice(string.ascii_letters) for x in range(512))
        )


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

    def test_compare_trees(self):
        file_a_path = get_named_tmpfile_path()
        file_b_path = get_named_tmpfile_path()

        fill_tmpfile(file_a_path)
        fill_tmpfile(file_b_path)

        file_a_instance = File(file_a_path)
        file_b_instance = File(file_b_path)

        tree_old_instance = Directory(
            {"a": Directory({}, {"file_a.txt": file_a_instance})}
        )

        tree_new_instance = Directory(
            {
                "a": Directory({}, {"file_a.txt": file_a_instance}),
                "b": Directory({}, {"file_b.txt": file_b_instance}),
            }
        )

        differences_instance = tree.compare_trees(
            Path(), tree_old_instance, tree_new_instance
        )

        expected_result = ["added: b/file_b.txt"]
        result = [
            differences.serialize_difference_as_message(x)
            for x in differences_instance.differences
        ]

        self.assertListEqual(result, expected_result)
