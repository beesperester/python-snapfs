from pathlib import Path
from typing import Any, Dict, Optional

from snapfs import transform, fs
from snapfs.datatypes import File


def store_file_as_blob(directory: Path, file: File) -> str:
    return fs.copy_file_as_blob(directory, file.path)


def load_blob_as_file(
    directory: Path, hashid: str, real_path: Optional[Path] = None
) -> File:
    hashid_path = directory.joinpath(transform.hashid_to_path(hashid))

    if real_path is None:
        real_path = hashid_path

    return File(real_path, True, hashid_path, hashid)


def serialize_file(file: File) -> str:
    return transform.file_to_hashid(file.path)


def file_as_dict(file: File) -> Dict[str, Any]:
    data = transform.as_dict(file)

    data["path"] = str(file.path)

    return data


def file_from_dict(data: Dict[str, Any]) -> File:
    return File(Path(data["path"]))
