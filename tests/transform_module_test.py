import unittest
import tempfile
import json

from pathlib import Path
from typing import List


from snapfs import fs, transform, stage
from snapfs.datatypes import Stage, File


def get_named_tmpfile_path():
    tmpfile = tempfile.NamedTemporaryFile(mode="wb", delete=False)
    # tmpfile.write(file_contents)
    tmpfile.close()

    return Path(tmpfile.name)


class TestTransformModule(unittest.TestCase):
    def test_apply(self):
        result = []

        def method(x):
            result.append(x + 1)

        data = [0, 1, 2, 3, 4]
        expected_result = [1, 2, 3, 4, 5]

        transform.apply(method, data)

        self.assertListEqual(result, expected_result)

    def test_as_dict(self):
        class Foobar:
            def __init__(self):
                self.name = "foo"

        foobar_instance = Foobar()

        expected_result = {"name": "foo"}

        result = transform.as_dict(foobar_instance)

        self.assertDictEqual(result, expected_result)

    def test_slug(self):
        expected_result = "fsfriendlypath"
        result = transform.slug("fs friendly-path")

        self.assertEqual(result, expected_result)

    def test_dict_as_json(self):
        data = {"foo": "bar"}

        expected_result = json.dumps(data, indent=2, sort_keys=True)
        result = transform.dict_as_json(data)

        self.assertEqual(result, expected_result)

    def test_hashid_as_path(self):
        data = "thisisahashid"

        expected_result = "th/isisahashid"
        result = transform.hashid_as_path(data)

        self.assertEqual(result, expected_result)

    def test_string_as_hashid(self):
        data = "this is a string"

        expected_result = (
            "bc7e8a24e2911a5827c9b33d618531ef094937f2b3803a591c625d0ede1fffc6"
        )
        result = transform.string_as_hashid(data)

        self.assertEqual(result, expected_result)

    def test_dict_as_hashid(self):
        data = {"foo": "bar"}

        expected_result = (
            "bbe8e9a86be651f9efc8e8df7fb76999d8e9a4a9674df9be8de24f4fb3d872a2"
        )
        result = transform.dict_as_hashid(data)

        self.assertEqual(result, expected_result)

    def test_file_as_hashid(self):
        data = b"this is some binary content"
        file_path = get_named_tmpfile_path()

        with open(file_path, "wb") as f:
            f.write(data)

        expected_result = (
            "6c0600f4ea7e8ece88b6c3935fca645317a74cb611a2c782affa17c2800d99d6"
        )

        result = transform.file_as_hashid(file_path)

        self.assertEqual(result, expected_result)

    def test_bytes_as_hashid(self):
        data = b"this is some binary content"

        expected_result = (
            "6c0600f4ea7e8ece88b6c3935fca645317a74cb611a2c782affa17c2800d99d6"
        )

        result = transform.bytes_as_hashid(data)

        self.assertEqual(result, expected_result)
