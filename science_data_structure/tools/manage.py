import click
from science_data_structure.author import Author
from science_data_structure.meta import Meta
from science_data_structure.config import ConfigManager
from science_data_structure.tools import files as file_tools
from pathlib import Path
from science_data_structure.structures import StructuredDataSet
import os


@click.group()
def manage():
    pass

@click.group()
def create():
    pass

@click.group()
def edit():
    pass

@click.group(name="global")
def _global():
    pass

@click.group(name="create")
def global_create():
    pass

@click.group(name="list")
def global_list():
    pass

@click.group(name="list")
def _list():
    pass

@click.command(name="dataset")
@click.argument("name")
@click.argument("description", required=False)
def create_dataset(name,
                   description):
    path = Path(os.getcwd())
    if (path / name / ".struct").exists():
        raise FileExistsError("There is already a dataset in this folder with that name")

    author = ConfigManager().default_author
    dataset = StructuredDataSet.create_dataset(path, name, Meta.create_top_level_meta(None, author))

    if description is not None:
        dataset.meta.description = description

    click.echo(dataset.path)
    dataset.write()


@click.command(name="meta")
def list_meta():
    meta = Meta.from_json(Path(os.getcwd()) / ".meta.json")
    click.echo(str(meta))

@click.command(name="author")
def list_author():
    meta = Meta.from_json(Path(os.getcwd()) / ".meta.json")
    authors = meta.authors
    authors = list(map(lambda x: str(x), authors))
    for author in authors:
        click.echo(author)

@click.command(name="author")
@click.argument("name", required=False)
def create_global_author(name):
    config_manager = ConfigManager()

    if name is None:
        name = click.prompt("What is the name of the new author?")

    author = Author.create_author(name)
    config_manager.default_author = author
    click.echo(config_manager._path)
    config_manager.write()

@click.command(name="author")
def list_global_author():
    config_manager = ConfigManager()
    click.echo("{:s}".format(str(config_manager.default_author)))

# globals
global_create.add_command(create_global_author)
global_list.add_command(list_global_author)

_global.add_command(global_create)
_global.add_command(global_list)
manage.add_command(_global)

# Create group
create.add_command(create_dataset)
manage.add_command(create)

# Delete group

# List group
_list.add_command(list_author)
_list.add_command(list_meta)
manage.add_command(_list)

# edit group
manage.add_command(edit)


if __name__ == "__main__":
    manage()
