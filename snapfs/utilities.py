from __future__ import annotations

import fnmatch
import json
import os
import re
import stat

from pathlib import Path
from typing import Callable, Dict, Any, List, Optional, TypeVar, Union

from snapfs.hash import hash_string
from snapfs.repository import Directory, File


T = TypeVar("T")


def slug(string: str) -> str:
    matches = re.findall(re.compile(r"(\w+)"), string)

    return "".join(list(matches))


def path_from_hash(hash: str, parts: int = 1, length: int = 2) -> str:
    return "/".join(
        [hash[i * length:(i * length) + length] for i in range(parts)]
        + [hash[parts * length:]]
    )


def make_dirs(path: Path):
    print(path)
    os.makedirs(
        path,
        mode=0o774,
        exist_ok=True
    )


def dict_to_json(data: Dict) -> str:
    return json.dumps(data, indent=2, sort_keys=True)


def save_file(file_path: Path, content: str, **kwargs) -> None:
    override = False

    if "override" in kwargs.keys():
        override = bool(kwargs["override"])

    if file_path.is_file() and override:
        # make file writeable
        os.chmod(file_path, stat.S_IWRITE | stat.S_IWGRP | stat.S_IROTH)

    if not file_path.is_file() or override:
        make_dirs(file_path.parent)

        with open(file_path, "w") as f:
            f.write(content)

        # make file read only
        os.chmod(file_path, stat.S_IREAD | stat.S_IRGRP | stat.S_IROTH)


def load_file(file_path: Path) -> Dict[str, Any]:
    data: Dict[str, Any] = {}

    with open(file_path, "r") as f:
        data = {
            **data,
            **json.load(f)
        }

    return data


def default(
    accessor: Callable[[], T],
    default: T
) -> T:
    value = None

    try:
        value = accessor()
    except Exception:
        pass

    if value is None:
        return default

    return value


def glob_filter(string: str, patterns: List[str]) -> bool:
    if not patterns:
        return True

    exclude = [x for x in patterns if not x.startswith("^")]
    include = [x[1:] for x in list(set(patterns) - set(exclude))]

    keep = not any([fnmatch.fnmatch(string, x) for x in exclude])

    if include:
        keep = any([fnmatch.fnmatch(string, x) for x in include])

    return keep


def load_ignore_file(directory: Path) -> List[str]:

    ignore_file_path = directory.joinpath(".ignore")

    if ignore_file_path.is_file():
        patterns = []

        with open(ignore_file_path, "r") as f:
            patterns = patterns + list(
                filter(
                    bool,
                    [
                        x.strip() for x in f.read().split("\n")
                        if not x.startswith("#")
                    ]
                )
            )

        return patterns

    raise Exception("No ignore file found")


def get_tree(
    current_path: Path,
    patterns: List[str] = []
) -> Directory:
    tree = Directory()

    # load ignore pattern
    try:
        patterns = load_ignore_file(current_path)
    except Exception:
        pass

    # add default ignores
    patterns = list(set(patterns + [".snapfs"]))

    for name in sorted(list(os.listdir(current_path))):
        item_path = Path(os.path.join(current_path, name))

        if item_path.is_file():
            if glob_filter(name, patterns):
                tree.files[name] = File(item_path)
        elif item_path.is_dir():
            result = get_tree(item_path, patterns)

            if result.files or result.directories:
                tree.directories[name] = result

    return tree
