from pathlib import Path

from snapfs import fs, transform, file
from snapfs.datatypes import Stage, File


def store_stage_as_file(path: Path, stage: Stage) -> None:
    data = transform.as_dict(stage)

    data["added_files"] = [file.serialize_file_as_dict(x) for x in stage.added_files]

    data["updated_files"] = [file.serialize_file_as_dict(x) for x in stage.updated_files]

    data["removed_files"] = [file.serialize_file_as_dict(x) for x in stage.removed_files]

    fs.save_data_as_file(path, data, override=True)


def load_file_as_stage(path: Path) -> Stage:
    data = fs.load_file_as_data(path)

    data["added_files"] = [file.deserialize_dict_as_file(x) for x in data["added_files"]]

    data["updated_files"] = [
        file.deserialize_dict_as_file(x) for x in data["updated_files"]
    ]

    data["removed_files"] = [
        file.deserialize_dict_as_file(x) for x in data["removed_files"]
    ]

    return Stage(**data)
