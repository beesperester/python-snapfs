from os import makedirs
import unittest
import tempfile
import json

from pathlib import Path
from typing import List


from snapfs import (
    fs,
    transform,
    branch,
    repository,
    head,
    tag,
    reference,
    commit,
    stage,
)
from snapfs.datatypes import Author, Branch, Commit, Stage, Tag, Head


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

    def test_get_branch_path(self):
        expected_result = "foobar/.snapfs/references/branches/main"

        result = str(repository.get_branch_path(Path("foobar"), "main", False))

        self.assertEqual(result, expected_result)

    def test_get_tag_path(self):
        expected_result = "foobar/.snapfs/references/tags/v1.0.0"

        result = str(repository.get_tag_path(Path("foobar"), "v1.0.0", False))

        self.assertEqual(result, expected_result)

    def test_get_commit_path(self):
        hashid = transform.string_as_hashid("test")

        expected_result = str(
            Path("foobar/.snapfs/blobs").joinpath(
                transform.hashid_as_path(hashid)
            )
        )

        result = str(repository.get_commit_path(Path("foobar"), hashid, False))

        self.assertEqual(result, expected_result)

    def test_get_head(self):
        head_instance = Head()

        expected_result = head.serialize_as_dict(head_instance)

        result = {}
        with tempfile.TemporaryDirectory() as tmpdirname:
            tmppath = Path(tmpdirname)

            head_path = repository.get_head_path(tmppath, False)

            makedirs(head_path.parent, exist_ok=True)

            head.store_as_file(head_path, head_instance)

            result = head.serialize_as_dict(repository.get_head(tmppath))

        self.assertEqual(result, expected_result)

    def test_get_branch(self):
        branch_instance = Branch()

        expected_result = branch.serialize_as_dict(branch_instance)

        result = {}
        with tempfile.TemporaryDirectory() as tmpdirname:
            tmppath = Path(tmpdirname)

            branch_path = repository.get_branch_path(tmppath, "main", False)

            makedirs(branch_path.parent, exist_ok=True)

            branch.store_as_file(branch_path, branch_instance)

            result = branch.serialize_as_dict(
                repository.get_branch(tmppath, "main")
            )

        self.assertEqual(result, expected_result)

    def test_get_tag(self):
        tag_instance = Tag()

        expected_result = tag.serialize_as_dict(tag_instance)

        result = {}
        with tempfile.TemporaryDirectory() as tmpdirname:
            tmppath = Path(tmpdirname)

            tag_path = repository.get_tag_path(tmppath, "v1.0.0", False)

            makedirs(tag_path.parent, exist_ok=True)

            tag.store_as_file(tag_path, tag_instance)

            result = tag.serialize_as_dict(
                repository.get_tag(tmppath, "v1.0.0")
            )

        self.assertEqual(result, expected_result)

    def test_get_reference(self):
        branch_instance = Branch()
        head_instance = Head("references/branches/main")

        expected_result = branch.serialize_as_dict(branch_instance)

        result = {}
        with tempfile.TemporaryDirectory() as tmpdirname:
            tmppath = Path(tmpdirname)

            # store branch
            branch_path = repository.get_branch_path(tmppath, "main", False)

            makedirs(branch_path.parent, exist_ok=True)

            branch.store_as_file(branch_path, branch_instance)

            # store head
            head_path = repository.get_head_path(tmppath, False)

            makedirs(head_path.parent, exist_ok=True)

            head.store_as_file(head_path, head_instance)

            result = reference.serialize_as_dict(
                repository.get_reference(tmppath)
            )

        self.assertEqual(result, expected_result)

    def test_get_commit(self):
        author_instance = Author("beesperester")

        commit_instance = Commit(author_instance, "initial commit")

        expected_result = commit.serialize_as_dict(commit_instance)

        result = {}
        with tempfile.TemporaryDirectory() as tmpdirname:
            tmppath = Path(tmpdirname)

            blobs_path = tmppath.joinpath(".snapfs/blobs")

            makedirs(blobs_path, exist_ok=True)

            hashid = commit.store_as_blob(blobs_path, commit_instance)

            result = commit.serialize_as_dict(
                commit.load_from_blob(
                    repository.get_commit_path(tmppath, hashid)
                )
            )

        self.assertEqual(result, expected_result)

    def test_get_latest_commit(self):
        author_instance = Author("beesperester")

        commit_instance = Commit(author_instance, "initial commit")

        expected_result = commit.serialize_as_dict(commit_instance)

        result = {}
        with tempfile.TemporaryDirectory() as tmpdirname:
            tmppath = Path(tmpdirname)

            # create commit blob
            blobs_path = repository.get_blobs_path(tmppath, False)

            makedirs(blobs_path, exist_ok=True)

            hashid = commit.store_as_blob(blobs_path, commit_instance)

            # create branch with commit hashid
            branch_path = repository.get_branch_path(tmppath, "main", False)

            makedirs(branch_path.parent, exist_ok=True)

            branch_instance = Branch(hashid)

            branch.store_as_file(branch_path, branch_instance)

            # create head with branch as ref
            head_path = repository.get_head_path(tmppath, False)

            makedirs(head_path.parent, exist_ok=True)

            head_instance = Head("references/branches/main")

            head.store_as_file(head_path, head_instance)

            result = commit.serialize_as_dict(
                repository.get_latest_commit(tmppath)
            )

        self.assertEqual(result, expected_result)

    def test_get_stage(self):
        stage_instance = Stage()

        expected_result = stage.serialize_as_dict(stage_instance)

        result = {}
        with tempfile.TemporaryDirectory() as tmpdirname:
            tmppath = Path(tmpdirname)

            stage_path = repository.get_stage_path(tmppath, False)

            makedirs(stage_path.parent)

            stage.store_as_file(stage_path, stage_instance)

            result = stage.serialize_as_dict(repository.get_stage(tmppath))

        self.assertDictEqual(result, expected_result)

    def test_store_stage(self):
        stage_instance = Stage()

        expected_result = stage.serialize_as_dict(stage_instance)

        result = {}
        with tempfile.TemporaryDirectory() as tmpdirname:
            tmppath = Path(tmpdirname)

            stage_path = repository.get_stage_path(tmppath, False)

            makedirs(stage_path.parent)

            repository.store_stage(tmppath, stage_instance)

            result = stage.serialize_as_dict(stage.load_from_file(stage_path))

        self.assertDictEqual(result, expected_result)
