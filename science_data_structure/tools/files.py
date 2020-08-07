from pathlib import Path
from science_data_structure.meta import Meta


def find_top_level_meta(path: Path):
    path = path.absolute()

    if (path / ".meta.json").exists():
        meta = Meta.from_json(path / ".meta.json")
        if meta.branch_id == 0:
            return meta
        return find_top_level_meta(path.parent)
    if str(path.parent) == "/":
        raise FileNotFoundError("This folder is not part of a dataset")
    return find_top_level_meta(path.parent)

