from pathlib import Path

from snapfs import fs, transform
from snapfs.datatypes import Head


def store_head_as_file(path: Path, head: Head) -> None:
    data = transform.as_dict(head)

    fs.save_data_as_file(path, data, override=True)


def load_file_as_head(path: Path) -> Head:
    return Head(**fs.load_file_as_data(path))
