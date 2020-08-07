import abc
from typing import Dict, List
from pathlib import Path
import os
import numpy
from science_data_structure.meta import Meta


class Node(abc.ABC):
    """
    Abstract class that forms the basic component
    of the structured data-set
    """
    @abc.abstractproperty
    def name(self) -> str:
        raise NotImplementedError("Name must be overriden")

    @abc.abstractproperty
    def path(self) -> Path:
        raise NotImplementedError("Path must be overridden")

    @abc.abstractmethod
    def read(self) -> "Node":
        raise NotImplementedError("read must be overriden")

    @abc.abstractproperty
    def meta(self):
        raise NotImplementedError("meta must be overriden")


class Branch(Node):
    """
    Branch of the tree represents a folder holder either
    more branches, or leafs, or a mix.
    """
    def __init__(self,
                 parent: Node,
                 name: str,
                 content: Dict[str, Node],
                 meta: Meta) -> None:
        self._parent = parent  # type: Node
        self._name = name  # type: str
        self._content = content  # type: Dict[str, Node]
        self._kill = []  # type: List[Node]
        self._meta = meta

    # Public functions
    def write(self) -> None:
        os.makedirs(self.path, exist_ok=True)
        self._meta.write()
        for node_name in self._content.keys():
            self._content[node_name].write()

    def add_branch(self,
                   name: str) -> "Branch":
        top_level_meta = self.top_level_meta
        meta = Meta.create_meta(top_level_meta, self.path / name)
        if name not in self._content:
            branch = Branch(self,
                            name,
                            {},
                            meta)
            self._content[name] = branch
            return  branch
        raise FileExistsError

    def add_data(self,
                 name: str,
                 data):
        meta = Meta.create_meta(self.top_level_meta, self.path / "{:s}.leaf".format(name))
        if name not in self._content:
            if isinstance(data, numpy.ndarray):
                data_node = LeafNumpy(self,
                                      name,
                                      meta)
                data_node.data = data
                self._content[name] = data_node
        return self._content[name]

    def read(self) -> "Branch":
        files = list(self.path.glob("*"))

        # branchs
        branchs = filter(lambda x: x.suffix != ".leaf" and not x.name.startswith("."), files)
        # data
        data = filter(lambda x: x.suffix == ".leaf" and not x.name.startswith("."), files)
        for branch in branchs:
            self._content[branch.name] = Branch(self.path, 
                                                branch.name,
                                            {})
            self._content[branch.name].read()

        for data_node in data:
            self._content[data_node.with_suffix("").name] = Leaf.initialize(data_node.with_suffix(""),
                                                                            data_node.with_suffix("").name)

    def keys(self) -> List[str]:
        return list(self._content.keys())

    # protected functions
    def _remove_item(self, key: str) -> Node:
        self._kill += [self._content[key]]
        return self._content.pop(key)

    def _remove(self) -> None:
        for key in self._content.keys():
            self._content[key]._remove()

        self._clear_kill()
        self.path.rmdir()

    def _clear_kill(self) -> None:
        for node in self._kill:
            node._remove()
            self._kill.remove(node)
        for branch in self.branches:
            branch._clear_kill()

    # Overriden functions
    def __getitem__(self, name: str) -> Node:
        try:
            return self._content[name]
        except KeyError:
            return self.add_branch(name)

    def __setitem__(self, key: str, item) -> None:
        if not isinstance(key, str):
            raise KeyError
        meta = Meta.create_meta(self.top_level_meta, self.path / "{:s}.leaf".format(key))

        if item is None:
            self._remove_item(key)
        elif not isinstance(item, Node):
            if isinstance(item, numpy.ndarray):
                if key not in self._content:
                    self._content[key] = LeafNumpy(self,
                                                   key,
                                                   meta)
                    self._content[key].data = item
                elif key in self._content:
                    self._kill += [self._content[key]]
                    self._content[key] = Leaf(self.path,
                                              key,
                                              meta)
                    self._content[key].data = item
                elif key not in self._content:
                    raise PermissionError
                else:
                    raise FileExistsError
        else:
            if key not in self._content:
                self._content[key] = Branch(self.path,
                                            key,
                                            meta)
            elif key in self._content:
                self._kill += [self._content[key]]
                self._content[key] = item
            elif key not in self._content:
                raise PermissionError
            else:
                raise FileExistsError

    def __eq__(self, other: "Branch") -> bool:
        if other == None or not isinstance(other, Branch):
            return False
        if self._name == other.name:
            if len(self.keys()) != len(other.keys()):
                return False
            for key in self.keys():
                if key not in other.keys():
                    return False

                if self._content[key] != other[key]:
                    return False
        else:
            return False
        return True

    def __str__(self) -> str:
        return "<branch: {:s} child_branches: {:d} child_leafs: {:d}>".format(self._name,
                                                                              len(self.branches),
                                                                              len(self.leafs))


    @property
    def name(self) -> str:
        return self._name

    @property
    def path(self) -> Path:
        return self._parent.path / self._name

    @property
    def has_leaves(self) -> bool:
        for key in self._content.keys():
            if isinstance(self._content[key], Branch):
                return True
        return False

    @property
    def branches(self) -> List["Branch"]:
        return list(filter(lambda content: isinstance(content, Branch),
                           self._content.values()))

    @property
    def leafs(self) -> List["Leaf"]:
        return list(filter(lambda content: isinstance(content, Leaf),
                           self._content.values()))

    @property
    def meta(self) -> Meta:
        return self._meta


    @property
    def top_level_meta(self) -> Meta:
        if isinstance(self, StructuredDataSet):
            return self.meta
        return self._parent.top_level_meta


class StructuredDataSet(Branch):
    """
    StructuredDataSet based on branch,
    only some functions are overridden for special
    functions.
    """
    def __init__(self,
                 path: Path,
                 name: str,
                 content: Dict[str, Node],
                 meta: Meta) -> None:
        super().__init__(self,
                         "{:s}.struct".format(name),
                         content,
                         meta)
        self._path = path
        
    def write(self) -> None:
        self.path.mkdir(exist_ok=True)
        self._meta.write()

        """
        # empty all the kill rings
        for node in self._kill:
            node._remove()
            self._kill.remove(node)

        for key in self._content.keys():
            self._content[key]._clear_kill()
        """
        for node_name in self._content.keys():
            self._content[node_name].write()

    def remove(self):
        self._remove()

    @staticmethod
    def read(path: Path) -> "StructuredDataSet":
        # load all the files
        files = list(path.glob("*"))

        # branches
        branches = list(filter(lambda x: x.suffix != ".leaf" and not x.name.startswith("."), files))

        # data
        data = list(filter(lambda x: x.suffix  == ".leaf" and not x.name.startswith("."), files))
        content = {}
        for branch in branches:
            content[branch.name] = Branch(path, 
                                      branch.name,
                                      {})
            content[branch.name].read()

        for data_node in data:
            content[data_node.with_suffix("").name] = Leaf.initialize(path.with_suffix(""),
                                                      data_node.name)

        return StructuredDataSet(path.parent, path.stem, content)

    @property
    def path(self) -> Path:
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
    """
    A leaf is a folder containing a single data-format, and description of the variable
    """
    def __init__(self, 
                 parent: Node,
                 name: str,
                 meta: Meta) -> None:
        self._parent = parent # type: Node
        self._name = name  # type: str
        self._meta = meta

        # class specific
        self._is_read = False  # type: bool
        self._is_changed = False  # type: bool

    # public functions
    def write(self) -> None:
        if not self.leaf_path.exists():
            self.leaf_path.mkdir()
        self._write_child()

    # properties
    @property
    def is_read(self) -> bool:
        return self._is_read

    @property
    def is_changed(self) -> bool:
        return self._is_changed

    @property
    def name(self) -> str:
        return self._name

    @property
    def leaf_path(self) -> Path:
        return self._parent.path / "{:s}.leaf".format(self._name)

    @property
    def data(self):
        return self._get_data()

    @data.setter
    def data(self, data):
        self._set_data(data)

    @property
    def meta(self) -> Meta:
        return self._meta

    # abstract methods
    @abc.abstractmethod
    def read(self) -> numpy.ndarray:
        raise NotImplementedError("Must override the read leaf read function")

    @abc.abstractmethod
    def _get_data(self):
        raise NotImplementedError("Must override the _get_data function")

    @abc.abstractmethod
    def _set_data(self, data):
        raise NotImplementedError("Must override the _set_data function")

    @abc.abstractmethod
    def _remove(self) -> None:
        raise NotImplementedError("Must override the _remove function")
   
    @abc.abstractmethod
    def _write_child(self) -> None:
        raise NotImplementedError("Must override the write function")

    @abc.abstractmethod
    def __eq__(self, other: "Leaf"):
        raise NotImplementedError("Must override the equal function")

    # static methods
    @staticmethod
    def initialize(path: Path,
                   name: str) -> "Leaf":
        name = name.replace(".leaf", "")

        # read all the non-hidden files
        content = list(path.with_suffix(".leaf").glob("./*"))
        content = list(filter(lambda x: not x.stem.startswith("."), content))

        if len(content) > 1:
            raise FileNotFoundError("To many files in the path: {:s}".format(str(path)))

        if len(content) > 0:
            if content[0].suffix == ".npy":
                return LeafNumpy(path.parent, name.replace(".leaf", ""))
        else:
            raise FileNotFoundError("The leaf does not exist {:s} {:s}".format(str(path), name))


    @property
    def meta(self) -> Meta:
        return self._meta


class LeafPandas(Leaf):
    """
    Class to hold data concerning the pandas data-frame
    """
    def __init__(parent_path: Path,
                 name: str) -> None:
        super().__init__(parent_path,
                         name)


class LeafNumpy(Leaf):
    """
    Class to hold data with the base numpy
    """
    def __init__(self,
                 parent: Node,
                 name: str,
                 meta: Meta) -> None:
        super().__init__(parent,
                         name,
                         meta)

        self._data = None  # type: numpy.ndarray

    # public functions
    def read(self) -> numpy.ndarray:
        self._data = numpy.load(self.path)
        self._is_read = True

    # protected functions
    def _get_data(self):
        if not self._is_read:
            self.read()
        return self._data

    def _set_data(self, data: numpy.ndarray) -> None:
        self._data = data
        self._is_changed = True

    def _remove(self) -> None:
        if self.path.exists():
            self.path.unlink()
            self.leaf_path.rmdir()
        elif self.path.exists():
            raise PermissionError
        elif not self.path.exists():
            raise FileNotFoundError("could not find: {:s}".format(str(self.path)))

    def _write_child(self) -> None:
        """
        Create a folder with the .leaf extension,
        place the numpy array inside,
        """
        self._meta.write()
        if self._is_changed:
            if not self.path.exists():
                numpy.save(self.path, self._data)

    # properties
    @property
    def path(self) -> Path:
        return self.leaf_path / "data.npy"

    # overridden functions
    def __eq__(self, other: "Leaf") -> bool:
        if isinstance(other, LeafNumpy):
            if self._name == other.name:
                if numpy.array_equal(self.data, other.data):
                    return True
        return False

    def __str__(self) -> str:
        return "<LeafNumpy {:s}>".format(str(self.path))

