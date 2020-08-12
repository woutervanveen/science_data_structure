import abc
from typing import Dict, List
from pathlib import Path
import os
from science_data_structure.meta import Meta


class Node:

    def __init__(self,
                 parent: "Node",
                 meta: Meta,
                 name: str):
        self._parent = parent
        self._meta = meta
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    @property
    def path(self) -> Path:
        return self._parent.path / self.name

    @abc.abstractmethod
    def write(self) -> "None":
        raise NotImplementedError("write functions must be overwritten")

    @abc.abstractmethod
    def remove(self) -> "None":
        raise NotImplementedError("remove function must be overwritten")

    @property
    def meta(self):
        return self._meta

    @property
    def top_level_meta(self) -> Meta:
        if isinstance(self, StructuredDataSet):
            return self.meta
        return self._parent.top_level_meta


class Branch(Node):

    def __init__(self,
                 parent: Node,
                 name: str,
                 content: Dict[str, Node],
                 meta: Meta) -> None:
        super().__init__(parent, meta, name)
        self._content = content  # type: Dict[str, Node]
        self._kill = []  # type: List[Node]

    def write(self) -> None:
        os.makedirs(self.path, exist_ok=True)
        self._meta.write()
        for node_name in self._content.keys():
            self._content[node_name].write()

        # empty the kill ring
        for node_kill in self._kill:
            node_kill.remove()
        self._kill = []

    def read(self) -> "Branch":
        content = list(self.path.glob("./*"))
        content = list(filter(lambda x: not x.stem.startswith("."), content))
        branches = list(filter(lambda x: x.suffix != ".leaf", content))
        data = list(filter(lambda x: x.suffix == ".leaf", content))

        for branch in branches:
            self._content[branch.name] = Branch(self,
                                                branch.name,
                                                {},
                                                Meta.from_json(self.path / branch.name / ".meta.json"))
            self._content[branch.name].read()

        for data_node in data:
            self._content[data_node.with_suffix("").name] = Leaf.initialize(self,
                                                                            data_node.with_suffix("").name)

    def keys(self) -> List[str]:
        return list(self._content.keys())

    def remove(self) -> None:
        for key in self._content.keys():
            self._content[key].remove()

        self.meta.path.unlink()
        self._clear_kill()
        self.path.rmdir()

    # protected functions
    def _remove_item(self, key: str) -> Node:
        self._kill += [self._content[key]]
        return self._content.pop(key)

    def _clear_kill(self) -> None:
        for node in self._kill:
            node._remove()
            self._kill.remove(node)
        for branch in self.branches:
            branch._clear_kill()

    def __getitem__(self, name: str) -> Node:
        try:
            return self._content[name]
        except KeyError:
            self._content[name] = Branch.create_branch(self, name)
            return self._content[name]

    def __setitem__(self, key: str, item) -> None:
        if not isinstance(key, str):
            raise KeyError
        if item is None:
            self._remove_item(key)
        elif not isinstance(item, Node):
            if key in self._content:
                self._kill += [self._content[key]]
            import data_formats
            self._content[key] = data_formats.available_types[type(item)](self,
                                                                          "{:s}.leaf".format(key),
                                                                          Meta.create_meta(self.top_level_meta,
                                                                                           self.path / "{:s}.leaf/".format(key)))
            self._content[key].data = item
        else:
            if key not in self._content:
                self._content[key] = item
            else:
                self._kill += [self._content[key]]
                self._content[key] = item

    @property
    def name(self) -> str:
        return self._name

    @property
    def branches(self) -> List["Branch"]:
        return list(filter(lambda content: isinstance(content, Branch),
                           self._content.values()))

    @property
    def leafs(self) -> List["Leaf"]:
        return list(filter(lambda content: isinstance(content, Leaf),
                           self._content.values()))

    @staticmethod
    def create_branch(parent: "Branch",
                      name: str) -> "Branch":
        return Branch(parent,
                      name,
                      {},
                      Meta.create_meta(parent.top_level_meta,
                                       parent.path / name))


class StructuredDataSet(Branch):

    def __init__(self,
                 path: Path,
                 name: str,
                 content: Dict[str, Node],
                 meta: Meta) -> None:
        super().__init__(None,
                         "{:s}.struct".format(name),
                         content,
                         meta)
        self._path = path

    @property
    def path(self):
        return self._path / self._name

    @staticmethod
    def create_dataset(path: Path,
                       name: str,
                       top_level_meta: Meta) -> "StructuredDataSet":
        path_tmp = path / "{:s}.struct".format(name)
        path_meta = path_tmp / ".meta.json"
        top_level_meta.path = path_meta

        return StructuredDataSet(path,
                                 name,
                                 {},
                                 top_level_meta)


class Leaf(Node):

    def __init__(self, 
                 parent: Node,
                 name: str,
                 meta: Meta) -> None:
        super().__init__(parent,
                         meta,
                         name)
      
    # public functions
    def write(self) -> None:
        if not self.path.exists():
            self.path.mkdir()
        self.meta.write()
        self._write_child()

    @property
    def data(self):
        return self._get_data()

    @data.setter
    def data(self, data):
        self._set_data(data)

    @abc.abstractmethod
    def _get_data(self):
        raise NotImplementedError("Must override the _get_data function")

    @abc.abstractmethod
    def _set_data(self, data):
        raise NotImplementedError("Must override the _set_data function")

    @staticmethod
    def initialize(parent: Node,
                   name: str) -> "Leaf":
        name = name.replace(".leaf", "")
        leaf_path = (parent.path / name).with_suffix(".leaf")
        meta = Meta.from_json(leaf_path / ".meta.json")

        # read all the non-hidden files
        content = list(leaf_path.with_suffix(".leaf").glob("./*"))
        content = list(filter(lambda x: not x.stem.startswith("."), content))

        if len(content) == 0:
            import data_formats
            return data_formats[content[0].suffix](parent, name.replace(".leaf"), meta)
        else:
            if len(content) > 1:
                raise FileNotFoundError("To many files in the leaf")
            else:
                raise FileNotFoundError("The leaf does not exist {:s} {:s}".format(str(leaf_path), name))
