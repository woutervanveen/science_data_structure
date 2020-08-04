import click
from science_data_structure.tools import config
from science_data_structure.author import Author

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


@click.command(name="author")
@click.argument("name")
def create_author(name: str):
    "Creates an author and saves it to disk"
    config_path = config.default_path() / "config.json"
    if config_path.exists():
        raise FileExistsError("There is already a registered author, please edit the author with the edit command")
    author = Author.create_author(name)

    config_file = config.ConfigFile(author,
                                    config_path)
    config_file.write()

@click.command(name="author")
@click.argument("name")
def edit_author(name: str):
    config_file = config.ConfigFile.read()
    config_file.author.name = name
    config_file.write(overwrite=True)


@click.command(name="author")
def list_author():
    config_file = config.ConfigFile.read()
    click.echo(str(config_file.author))


# Create group
create.add_command(create_author)
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
