# cure_ground/core/protocols/states/loader.py
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Union

import yaml


@dataclass(frozen=True)
class StateDef:
    name: str
    id: int
    description: Optional[str] = None


class States:
    """
    Accessor for flight states loaded from YAML.
    - Avoids dynamic attribute injection to keep static analyzers happy.
    - Provides lookups by name or id, friendly errors, and iteration helpers.
    """

    def __init__(self, state_defs: List[dict]):
        by_name: Dict[str, StateDef] = {}
        by_id: Dict[int, StateDef] = {}

        # Normalize + validate
        for raw in state_defs:
            name = raw["name"]
            sid = int(raw["id"])
            desc = raw.get("description")
            s = StateDef(name=name, id=sid, description=desc)

            if name in by_name:
                raise ValueError(f"Duplicate state name: {name!r}")
            if sid in by_id:
                raise ValueError(f"Duplicate state id: {sid}")

            by_name[name] = s
            by_id[sid] = s

        self._by_name = by_name
        self._by_id = by_id

    # --- Lookups ---
    def get(self, name: str) -> StateDef:
        try:
            return self._by_name[name]
        except KeyError:
            raise KeyError(self._unknown_name_msg(name))

    def get_by_id(self, state_id: int) -> StateDef:
        try:
            return self._by_id[state_id]
        except KeyError:
            raise KeyError(self._unknown_id_msg(state_id))

    def get_id(self, name: str) -> int:
        return self.get(name).id

    def get_name(self, state_id: int) -> str:
        return self.get_by_id(state_id).name

    # --- Introspection ---
    def names(self) -> List[str]:
        return list(self._by_name.keys())

    def ids(self) -> List[int]:
        return list(self._by_id.keys())

    def items(self) -> Iterable[StateDef]:
        # Stable iteration by id
        for sid in sorted(self._by_id):
            yield self._by_id[sid]

    # --- Mapping-style sugar ---
    def __getitem__(self, key: Union[str, int]) -> StateDef:
        if isinstance(key, str):
            return self.get(key)
        elif isinstance(key, int):
            return self.get_by_id(key)
        raise TypeError(f"Key must be str (name) or int (id); got {type(key).__name__}")

    # --- Error helpers ---
    def _unknown_name_msg(self, name: str) -> str:
        return f"Unknown state name {name!r}. Valid: {', '.join(self.names())}"

    def _unknown_id_msg(self, sid: int) -> str:
        return f"Unknown state id {sid}. Valid: {', '.join(map(str, self.ids()))}"


def load_states(version: int) -> States:
    """
    Load the YAML-defined states for a given version.
    Mirrors your DataNames loader’s versioning scheme.
    """
    version_str = str(version).zfill(2)
    yaml_path = f"cure_ground/core/protocols/states/states_v{version_str}.yaml"
    with open(yaml_path, "r") as f:
        cfg = yaml.safe_load(f)

    try:
        state_defs = cfg["states"]
    except KeyError as e:
        raise ValueError(
            f"Invalid states YAML at {yaml_path}: missing 'states' list"
        ) from e

    return States(state_defs)


def get_list_of_available_states_configs() -> List[str]:
    """
    Find available YAML configs (e.g., ['01', '02']).
    """
    folder_path = "cure_ground/core/protocols/states"
    versions: List[str] = []
    for fname in os.listdir(folder_path):
        if fname.startswith("states_v") and fname.endswith(".yaml"):
            versions.append(fname.split("_v")[1].split(".yaml")[0])
    versions.sort()
    return versions
