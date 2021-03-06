import os
import unittest
import tempfile
import json
import random
import string

from pathlib import Path
from typing import List


from snapfs import (
    fs,
    transform,
    stage,
    directory,
    file,
    differences,
)
from snapfs.datatypes import File, Directory


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
    def test_store_as_blob(self):
        directory_instance = Directory()

        result = ""
        expected_result = transform.string_as_hashid(
            transform.dict_as_json(
                directory.serialize_as_dict(directory_instance)
            )
        )

        with tempfile.TemporaryDirectory() as tmpdirname:
            result = directory.store_as_blob(
                Path(tmpdirname), directory_instance
            )

        self.assertEqual(result, expected_result)

    def test_load_from_blob(self):
        directory_instance = Directory()

        result = {}
        expected_result = {"directories": {}, "files": {}}

        with tempfile.TemporaryDirectory() as tmpdirname:
            directory_hashid = directory.store_as_blob(
                Path(tmpdirname), directory_instance
            )

            result = directory.serialize_as_dict(
                directory.load_from_blob(Path(tmpdirname), directory_hashid)
            )

        self.assertDictEqual(result, expected_result)

    def test_serialize_as_hashid(self):
        directory_instance = Directory()

        data = {"directories": {}, "files": {}}

        expected_result = transform.dict_as_hashid(data)
        result = directory.serialize_as_hashid(directory_instance)

        self.assertEqual(result, expected_result)

    def test_serialize_as_dict(self):
        directories = {"test": Directory()}

        directory_instance = Directory(directories)

        expected_result = {
            "directories": {"test": {"directories": {}, "files": {}}},
            "files": {},
        }

        result = directory.serialize_as_dict(directory_instance)

        self.assertDictEqual(result, expected_result)

    def test_transform_as_list(self):
        file_a_instance = File(Path("file_a"))
        file_b_instance = File(Path("foobar/file_b"))

        directory_instance = Directory(
            {"foobar": Directory({}, {"file_b": file_b_instance})},
            {"file_a": file_a_instance},
        )

        expected_result = [
            file.serialize_as_dict(file_b_instance),
            file.serialize_as_dict(file_a_instance),
        ]
        result = [
            file.serialize_as_dict(x)
            for x in directory.transform_as_list(Path(), directory_instance)
        ]

        self.assertListEqual(result, expected_result)

    def test_transform_from_list(self):
        file_instance = File(Path("test/foobar"))

        data = [file_instance]

        expected_result = {
            "directories": {
                "test": {
                    "directories": {},
                    "files": {"foobar": file.serialize_as_dict(file_instance)},
                }
            },
            "files": {},
        }
        result = directory.serialize_as_dict(
            directory.transform_from_list(Path(), data)
        )

        self.assertEqual(result, expected_result)

    def test_load_from_directory_path(self):
        directory_instance = Directory()
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

            directory_instance = directory.load_from_directory_path(
                Path(tmpdirname)
            )

        expected_result = {
            "directories": {
                "test": {
                    "directories": {},
                    "files": {
                        "foo.c4d": file.serialize_as_dict(File(fake_file_path))
                    },
                }
            },
            "files": {},
        }

        result = directory.serialize_as_dict(directory_instance)

        self.assertDictEqual(result, expected_result)

    def test_compare(self):
        file_a_path = get_named_tmpfile_path()
        file_b_path = get_named_tmpfile_path()
        file_c_path = get_named_tmpfile_path()

        fill_tmpfile(file_a_path)
        fill_tmpfile(file_b_path)

        file_a_instance = File(
            file_a_path, True, Path(), transform.string_as_hashid("foo")
        )
        file_b_instance = File(file_b_path)
        file_c_instance = File(file_c_path)
        file_a_modified_instance = File(
            file_a_path, True, Path(), transform.string_as_hashid("bar")
        )

        directory_old_instance = Directory(
            {
                "a": Directory(
                    {},
                    {
                        "file_a.txt": file_a_instance,
                        "file_c.txt": file_c_instance,
                    },
                )
            }
        )

        directory_new_instance = Directory(
            {
                "a": Directory({}, {"file_a.txt": file_a_modified_instance}),
                "b": Directory({}, {"file_b.txt": file_b_instance}),
            }
        )

        differences_instance = directory.compare(
            Path(), directory_old_instance, directory_new_instance
        )

        expected_result = [
            "added: b/file_b.txt",
            "updated: a/file_a.txt",
            "removed: a/file_c.txt",
        ]
        result = differences.serialize_as_messages(differences_instance)

        self.assertListEqual(result, expected_result)
