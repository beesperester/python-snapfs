from pathlib import Path

from snapfs import fs, transform
from snapfs.dataclasses import Stage, File


def store_stage_as_file(path: Path, stage: Stage) -> None:
    data = transform.as_dict(stage)

    data["files"] = [transform.as_dict(x) for x in stage.files]

    fs.save_data_as_file(path, data, override=True)


def load_file_as_stage(path: Path) -> Stage:
    data = fs.load_file_as_data(path)

    data["files"] = [File(x) for x in data["files"]]

    return Stage(**data)
