from pathlib import Path
from typing import Any, Dict, Optional

from snapfs import transform, fs
from snapfs.datatypes import File


def store_file_as_blob(directory: Path, file: File) -> str:
    if file.is_blob:
        # if file has been loaded as blob simply
        # return the associated hashid
        return file.hashid

    return fs.copy_file_as_blob(directory, file.path)


def load_blob_as_file(
    directory: Path, hashid: str, real_path: Optional[Path] = None
) -> File:
    hashid_path = directory.joinpath(transform.hashid_to_path(hashid))

    if real_path is None:
        real_path = hashid_path

    return File(real_path, True, hashid_path, hashid)


def serialize_file_as_hashid(file: File) -> str:
    if file.is_blob:
        # if file has been loaded as blob simply
        # return the associated hashid
        return file.hashid

    return transform.file_to_hashid(file.path)


def serialize_file_as_dict(file: File) -> Dict[str, Any]:
    data = transform.as_dict(file)

    data = {
        **data,
        "path": str(file.path),
        "blob_path": str(file.blob_path) if file.blob_path else None,
    }

    return data


def deserialize_dict_as_file(data: Dict[str, Any]) -> File:
    return File(Path(data["path"]))
