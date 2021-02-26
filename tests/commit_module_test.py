import unittest
import tempfile

from pathlib import Path
from typing import List


from snapfs import commit, transform
from snapfs.datatypes import Commit, Author


author_instance = Author("beesperester")

expected_result = {
    "author": {"name": "beesperester", "fullname": "", "email": ""},
    "message": "initial commit",
    "tree_hashid": "",
    "previous_commits_hashids": [],
}

commit_instance = Commit(author_instance, "initial commit")


class TestCommitModule(unittest.TestCase):
    def test_commit_datatype(self):
        self.assertDictEqual(
            commit.serialize_as_dict(commit_instance),
            expected_result,
        )

    def test_store_as_blob(self):
        commit_hashid = ""

        with tempfile.TemporaryDirectory() as tmpdirname:
            commit_hashid = commit.store_as_blob(
                Path(tmpdirname), commit_instance
            )

        self.assertEqual(
            commit_hashid,
            transform.string_as_hashid(
                transform.dict_as_json(expected_result)
            ),
        )

    def test_load_from_blob(self):
        commit_dict = {}

        with tempfile.TemporaryDirectory() as tmpdirname:
            commit_hashid = commit.store_as_blob(
                Path(tmpdirname), commit_instance
            )

            commit_dict = commit.load_from_blob(
                Path(tmpdirname).joinpath(
                    transform.hashid_as_path(commit_hashid)
                )
            )

        self.assertDictEqual(
            commit.serialize_as_dict(commit_dict), expected_result
        )
