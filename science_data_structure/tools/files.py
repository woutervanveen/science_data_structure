from pathlib import Path
import click

APP_NAME = "science_data_structure"


def config_location() -> Path:
    path = Path(click.get_app_dir(APP_NAME))
    path.mkdir(exist_ok=True)
    return path


def find_top_level_meta(path: Path):
    from science_data_structure.meta import Meta

    path = path.absolute()

    if (path / ".meta.json").exists():
        meta = Meta.from_json(path / ".meta.json")
        if meta.branch_id == 0:
            return meta
        return find_top_level_meta(path.parent)
    if str(path.parent) == "/":
        raise FileNotFoundError("This folder is not part of a dataset")
    return find_top_level_meta(path.parent)


def get_folder_size(path: Path):
    folder_size = path.stat().st_size

    for child in path.iterdir():
        if child.is_dir():
            folder_size += get_folder_size(child)
        else:
            folder_size += child.stat().st_size

    return folder_size


def set_file_properties(path: Path, dig: bool = True) -> int:
    """
    Compute the size of the current branch, including all the subbranches
    The meta files of the subbranches is also updated
    """
    from science_data_structure.meta import Meta, FileProperty
    meta = Meta.from_json(path / ".meta.json")
    
    folder_size = path.stat().st_size
    for child in path.iterdir():
        if child.is_dir():
            if dig:
                folder_size += set_file_properties(child)
            else:
                folder_size += get_folder_size(child)
        else:
            folder_size += child.stat().st_size

    folders_in_path = list(filter(lambda x: x.is_dir(), list(path.iterdir())))
    # create the file properties node
    file_properties = FileProperty()
    file_properties.size = folder_size
    file_properties.n_childs = len(folders_in_path)

    meta.add_property(file_properties)

    return folder_size

