from pathlib import Path
from typing import Any, Dict

from snapfs import fs, transform, file
from snapfs.datatypes import Stage, File


def store_stage_as_file(path: Path, stage: Stage) -> None:
    fs.store_dict_as_file(path, serialize_stage_as_dict(stage), override=True)


def serialize_stage_as_dict(stage: Stage) -> Dict[str, Any]:
    data = transform.as_dict(stage)

    return {
        **data,
        "added_files": [
            file.serialize_file_as_dict(x) for x in stage.added_files
        ],
        "updated_files": [
            file.serialize_file_as_dict(x) for x in stage.updated_files
        ],
        "removed_files": [
            file.serialize_file_as_dict(x) for x in stage.removed_files
        ],
    }


def deserialize_dict_as_stage(data: Dict[str, Any]) -> Stage:
    return Stage(
        **{
            **data,
            "added_files": [
                file.deserialize_dict_as_file(x) for x in data["added_files"]
            ],
            "updated_files": [
                file.deserialize_dict_as_file(x) for x in data["updated_files"]
            ],
            "removed_files": [
                file.deserialize_dict_as_file(x) for x in data["removed_files"]
            ],
        }
    )


def load_file_as_stage(path: Path) -> Stage:
    return deserialize_dict_as_stage(fs.load_file_as_dict(path))
