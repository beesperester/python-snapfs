from __future__ import annotations
import dataclasses

from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class File:
    path: Path


@dataclass
class Directory:
    directories: Dict[str, Directory] = field(default_factory=dict)
    files: Dict[str, File] = field(default_factory=dict)


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
    previous_commits_hashids: List[str] = field(default_factory=list)


@dataclass
class Head:
    ref: str = ""


@dataclass
class Branch:
    commit_hashid: str = ""


@dataclass
class Tag:
    message: str
    commit_hashid: str = ""


@dataclass
class Stage:
    added_files: List[Path] = field(default_factory=list)
    updated_files: List[Path] = field(default_factory=list)
    removed_files: List[Path] = field(default_factory=list)


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


@dataclass
class Differences:
    differences: List[Difference] = field(default_factory=list)
