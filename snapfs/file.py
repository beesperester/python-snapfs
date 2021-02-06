from pathlib import Path

from snapfs import transform, fs
from snapfs.dataclasses import File


def store_file_as_blob(directory: Path, file: File) -> str:
    return fs.copy_file_as_blob(directory, file.path)


def load_blob_as_file(directory: Path, hashid: str) -> File:
    hashid_path = directory.joinpath(
        transform.hashid_to_path(hashid)
    )

    return File(hashid_path)


def serialize_file(file: File) -> str:
    return transform.file_to_hashid(file.path)
