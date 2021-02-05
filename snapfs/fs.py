import stat
import shutil

from pathlib import Path

from snapfs import transform, hash


def make_dirs(path: Path):
    path.mkdir(0o774, True, True)


def save_file(file_path: Path, content: str, override: bool = False) -> None:
    if file_path.is_file() and override:
        print("override", file_path)
        # make file writeable
        file_path.chmod(stat.S_IWRITE | stat.S_IWGRP | stat.S_IROTH)

    if not file_path.is_file() or override:
        make_dirs(file_path.parent)

        with open(file_path, "w") as f:
            f.write(content)

        # make file read only
        file_path.chmod(stat.S_IREAD | stat.S_IRGRP | stat.S_IROTH)


def save_blob(directory: Path, data: dict) -> str:
    data_string = transform.dict_to_json(data)

    data_hash = hash.hash_string(data_string)

    blob_path = directory.joinpath(transform.hashid_to_path(data_hash))

    save_file(blob_path, data_string)

    return data_hash


def load_file(file_path: Path) -> str:
    data: str = ""

    with open(file_path, "r") as f:
        data = f.read()

    return data


def copy_file(source: Path, target: Path) -> None:
    shutil.copyfile(source, target)


def copy_file_as_blob(source: Path, target: Path) -> None:
    copy_file(source, target)

    target.chmod(stat.S_IREAD | stat.S_IRGRP | stat.S_IROTH)
