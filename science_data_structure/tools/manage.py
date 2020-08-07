import click
from science_data_structure.tools import config
from science_data_structure.author import Author
from science_data_structure.meta import Meta
from science_data_structure.tools import files
from pathlib import  Path
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

@click.group(name="list")
def _list():
    pass

@click.command(name="dataset")
@click.argument("name")
@click.argument("author")
def create_dataset(name, author):
    path = Path(os.getcwd())
    if (path / name / ".struct").exists():
        raise FileExistsError("There is already a dataset in this folder with that name")

    author = Author.create_author(author)
    dataset = StructuredDataSet.create_dataset(path, name, Meta.create_top_level_meta(None, author))

    click.echo(dataset.path)
    dataset.write()

@click.command(name="author")
def create_author():
    meta = files.find_top_level_meta(Path(os.getcwd()))
    value = click.prompt("What is the name of the author?")
    if value != "":
        # first check if the author name is not already registered
        for author in meta.authors:
            if author.name == value:
                click.echo("This name is already registered in this dataset")
            else:
                author = Author.create_author(value)
                meta.authors.append(author)
                meta.write()

@click.command(name="author")
def edit_author():
    meta = files.find_top_level_meta(Path(os.getcwd()))
    for i_author, author in enumerate(meta.authors):
        click.echo("{:d} \t {:s}\n".format(i_author, str(author.name)))
    value = click.prompt("Which user you want to edit?", type=int)
    if value >= 0 and value < len(meta.authors):
        name_new = click.prompt("What is the new name of the author?", type=str)
        meta.authors[value].name = name_new
        meta.write()
    else:
        click.echo("Please entery a value id from the list")
    

@click.command(name="author")
def list_author():
    meta = files.find_top_level_meta(Path(os.getcwd()))
    print("In total {:d} authors are registered in this data-set".format(len(meta.authors)))
    for author in meta.authors:
        click.echo(str(author))

# Create group
create.add_command(create_author)
create.add_command(create_dataset)
manage.add_command(create)

# Delete group

# List group
_list.add_command(list_author)
manage.add_command(_list)

# edit group
edit.add_command(edit_author)
manage.add_command(edit)


if __name__ == "__main__":
    manage()
