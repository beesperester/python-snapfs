from __future__ import annotations

from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List


@dataclass
class File:
    path: Path


@dataclass
class Directory:
    directories: Dict[str, Directory]
    files: Dict[str, File]


@dataclass
class Author:
    name: str
    fullname: str = ""
    email: str = ""


@dataclass
class Commit:
    author: Author
    message: str
    tree_hashid: str = ""
    previous_commit_hashid: str = ""


@dataclass
class Head:
    ref: str


@dataclass
class Branch:
    commit_hashid: str = ""


@dataclass
class Tag:
    message: str
    commit_hashid: str = ""


@dataclass
class Stage:
    files: List[File]


@dataclass
class Difference:
    path: Path


@dataclass
class FileAddedDifference(Difference):
    """
    This class represents a file added message
    """


@dataclass
class FileUpdatedDifference(Difference):
    """
    This class represents a file updated message
    """


@dataclass
class FileRemovedDifference(Difference):
    """
    This class represents a file removed message
    """
