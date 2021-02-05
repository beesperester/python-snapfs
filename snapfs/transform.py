from __future__ import annotations

import json

from typing import Dict, Optional, Type, Union

JsonDict = Dict[str, Optional[Union[str, int, float, "JsonDict"]]]


def dict_to_json(data: JsonDict) -> str:
    return json.dumps(data, indent=2, sort_keys=True)


def json_to_dict(data: str) -> JsonDict:
    return json.loads(data)


def hashid_to_path(hashid: str, parts: int = 1, length: int = 2) -> str:
    return "/".join(
        [hashid[i * length:(i * length) + length] for i in range(parts)]
        + [hashid[parts * length:]]
    )
