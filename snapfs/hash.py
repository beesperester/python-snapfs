import os
import json
import fnmatch

from collections import OrderedDict
from typing import OrderedDict as OrderedDictType

from hashlib import sha256
from pathlib import Path

from snapfs.config import config


def hash_string(string: str) -> str:
    sha256_hash = sha256()

    sha256_hash.update(string.encode("utf-8"))

    return sha256_hash.hexdigest()


def hash_file(path: Path) -> str:
    assert path.is_file()

    sha256_hash = sha256()

    with open(str(path), "rb") as f:
        # Read and update hash string value in blocks of 4K
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)

    return sha256_hash.hexdigest()


def hash_directory(hashpath: Path) -> str:
    directory: OrderedDictType[str, str] = OrderedDict()

    for root, directories, files in os.walk(
        str(hashpath),
        followlinks=True
    ):
        for filename in sorted(files):
            if any([fnmatch.fnmatch(filename, x) for x in config.ignore]):
                continue

            filepath = Path(os.path.join(root, filename))

            directory[filename] = hash_file(filepath)

        for directoryname in sorted(directories):
            if any([fnmatch.fnmatch(directoryname, x) for x in config.ignore]):
                continue

            directorypath = Path(os.path.join(root, directoryname))

            directory[directoryname] = hash_directory(directorypath)

    return hash_string(json.dumps(directory))


if __name__ == "__main__":
    # print(hash_file(Path(__file__)))

    print(hash_directory(
        Path(os.path.join(os.getcwd(), "snapfs"))
    ))
