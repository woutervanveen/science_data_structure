import abc
from typing import Dict, List
from pathlib import Path
import os
import numpy


class Node(abc.ABC):
    """
    Abstract class that forms the basic component
    of the structured data-set
    """
    @abc.abstractproperty
    def name(self) -> str:
        pass

    @abc.abstractproperty
    def path(self) -> Path:
        pass

    @abc.abstractmethod
    def read(self) -> "Node":
        pass


class Branch(Node):
    """
    Branch of the tree represents a folder holder either
    more branches, or leafs, or a mix.
    """
    def __init__(self,
                 parent_path: Path,
                 name: str,
                 content: Dict[str, Node],
                 overwrite: bool = False) -> None:
        self._parent_path = parent_path  # type: Path
        self._name = name  # type: str
        self._content = content  # type: Dict[str, Node]
        self._overwrite = overwrite
        self._kill = []  # type: List[Node]

    # Public functions
    def write(self) -> None:
        os.makedirs(self.path, exist_ok=True)
        for node_name in self._content.keys():
            self._content[node_name].write()

    def add_branch(self,
                 name: str) -> "Branch":
        if name not in self._content or self._overwrite:
            branch = Branch(self.path,
                        name,
                        {})
            self._content[name] = branch
            return  branch
        raise FileExistsError

    def add_data(self,
                 name: str,
                 data):
        if name not in self._content or self._overwrite:
            if isinstance(data, numpy.ndarray):
                data_node = LeafNumpy(self.path,
                                      name,
                                      overwrite=self._overwrite)
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
        if self._overwrite:
            self._kill += [self._content[key]]
            return self._content.pop(key)
        raise PermissionError

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

        if item is None:
            if self._overwrite:
                self._remove_item(key)
            else:
                raise PermissionError
        elif not isinstance(item, Node):
            if isinstance(item, numpy.ndarray):
                if key not in self._content:
                    self._content[key] = LeafNumpy(self.path,
                                                   key)
                    self._content[key].data = item
                elif key in self._content and self._overwrite:
                    self._kill += [self._content[key]]
                    self._content[key] = Leaf(self.path,
                                              key)
                    self._content[key].data = item
                elif key not in self._content:
                    raise PermissionError
                else:
                    raise FileExistsError
        else:
            if key not in self._content:
                self._content[key] = Branch(self.path,
                                          key)
            elif key in self._content and self._overwrite:
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


    # properties
    @property
    def overwrite(self) -> bool:
        return self._overwrite

    @overwrite.setter
    def overwrite(self, overwrite: bool) -> None:
        self._overwrite = overwrite
        for key in self._content.keys():
            self._content[key].overwrite = overwrite

    @property
    def name(self) -> str:
        return self._name

    @property
    def path(self) -> Path:
        return self._parent_path / self._name

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
                 overwrite: bool = False) -> None:
        super().__init__(path,
                         "{:s}.struct".format(name),
                         content,
                         overwrite=overwrite)

    def write(self, 
              exist_ok: bool =False) -> None:
        if self.path.exists and not exist_ok:
            raise FileExistsError
        self.path.mkdir(exist_ok=True)

        # empty all the kill rings
        for node in self._kill:
            node._remove()
            self._kill.remove(node)

        for key in self._content.keys():
            self._content[key]._clear_kill()

        for node_name in self._content.keys():
            self._content[node_name].write()

    def remove(self):
        if self._overwrite:
            self._remove()
        else:
            raise PermissionError

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

    
class Leaf(Node):
    """
    A leaf is a folder containing a single data-format, and description of the variable
    """
    def __init__(self, 
                 parent_path: Path,
                 name: str,
                 overwrite: bool = False) -> None:
        self._parent_path = parent_path  # type: Path
        self._name = name  # type: str
        self._overwrite = overwrite  # type: bool

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
        return self._parent_path / "{:s}.leaf".format(self._name)

    @property
    def overwrite(self) -> bool:
        return self._overwrite

    @overwrite.setter
    def overwrite(self, overwrite: bool) -> None:
        self._overwrite = overwrite

    @property
    def data(self):
        return self._get_data()

    @data.setter
    def data(self, data):
        self._set_data(data)

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

    @abc.abstractproperty
    def path(self) -> Path:
        raise NotImplementedError("Path not implemented")

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
                 parent_path: Path,
                 name: str,
                 overwrite: bool = False) -> None:
        super().__init__(parent_path,
                         name,
                         overwrite=overwrite)

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
        if self.path.exists() and self._overwrite:
            self.path.unlink()
            self.leaf_path.rmdir()
        elif self.path.exists() and not self._overwrite:
            raise PermissionError
        elif not self.path.exists():
            raise FileNotFoundError("could not find: {:s}".format(str(self.path)))

    def _write_child(self) -> None:
        """
        Create a folder with the .leaf extension,
        place the numpy array inside,
        """
        if self._is_changed:
            if not self.path.exists() or self._overwrite:
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

