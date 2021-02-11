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


class TestStageModule(unittest.TestCase):