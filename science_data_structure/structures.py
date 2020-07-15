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

class Leaf(Node):

    def __init__(self,
                 parent_path: Path,
                 name: str,
                 content: Dict[str, Node],
                 enable_auto_branching: bool = True,
                 overwrite: bool = False) -> None:
        self._parent_path = parent_path  # type: Path
        self._name = name  # type: str
        self._content = content  # type: Dict[str, Node] 
        self._enable_auto_branching = enable_auto_branching
        self._overwrite = overwrite
        self._kill = []  # type: List[Node]

    @property
    def name(self) -> str:
        return self._name

    @property
    def path(self) -> Path:
        return self._parent_path / self._name
    
    def write(self) -> None:
        os.makedirs(self.path, exist_ok=True)
        for node_name in self._content.keys():
            self._content[node_name].write()

    def add_leaf(self,
                 name: str) -> "Leaf":
        if name not in self._content or self._overwrite:
            leaf = Leaf(self.path,
                        name,
                        {})
            self._content[name] = leaf
            return  leaf
        raise FileExistsError

    def add_data(self,
                 name: str,
                 data: numpy.ndarray):
        if name not in self._content or self._overwrite:
            data_node = Data(self.path, name)
            data_node.data = data
            self._content[name] = data_node
        return self._content[name]

    def read(self) -> "Leaf":
        files = list(self.path.glob("*"))

        # leafs
        leafs = filter(lambda x: x.is_dir(), files)

        # data
        data = filter(lambda x: x.suffix == ".npy", files)

        for leaf in leafs:
            self._content[leaf.name] = Leaf(self.path, 
                                            leaf.name,
                                            {})
            self._content[leaf.name].read()

        for data_node in data:
            self._content[data_node.stem] = Data(self.path,
                                            data_node.stem)
    def __getitem__(self, name: str) -> Node:
        try:
            return self._content[name]
        except KeyError:
            # the variable does not exist
            if self._enable_auto_branching:
                # create a new leaf based on the name provided
                return self.add_leaf(name)

        raise KeyError

    def __setitem__(self, key: str, item) -> None:
        """
        TODO check if the key is of value string
        TODO handle setting leaf or node with None
        TODO handle the deletion of the node when it is overwritten by another node
        """
        if not isinstance(item, Node):
            if isinstance(item, numpy.ndarray):
                if self._enable_auto_branching and key not in self._content:
                    self._content[key] = Data(self.path,
                                              key)
                elif key in self._content and self._overwrite:
                    self._kill += [self._content[key]]
                    self._content[key] = Data(self.path,
                                              key)
                elif key not in self._content:
                    raise PermissionError
                else:
                    raise FileExistsError
        else:
            if self._enable_auto_branching and key not in self._content:
                self._content[key] = Leaf(self.path,
                                          key)
            elif key in self._content and self._overwrite:
                self._kill += [self._content[key]]
                self._content[key] = Leaf(self.path,
                                          key)
            elif key not in self._content:
                raise PermissionError
            else:
                raise FileExistsError

    @property
    def enable_auto_branching(self) -> bool:
        return self._enable_auto_branching

    @enable_auto_branching.setter
    def enable_auto_branching(self, enable_auto_branching) -> None:
        self._enable_auto_branching = enable_auto_branching

        for key in self._content.keys():
            if isinstance(self._content[key], Leaf):
                self._content[key].enable_auto_branching = enable_auto_branching

    @property
    def overwrite(self) -> bool:
        return self._overwrite

    @overwrite.setter
    def overwrite(self, overwrite: bool) -> None:
        self._overwrite = overwrite
        for key in self._content.keys():
            if isinstance(self._content[key], Leaf):
                self._content[key].overwrite = overwrite


    def keys(self) -> List[str]:
        return list(self._content.keys())


class StructuredDataset(Leaf):
    """
    StructuredDataset the base class of Leaf
    """
    def __init__(self,
                 path: Path,
                 name: str,
                 content: Dict[str, Node],
                 enable_auto_branching: bool = True,
                 overwrite: bool = False) -> None:
        super().__init__(path , "{:s}.struct".format(name),
                         content,
                         enable_auto_branching = enable_auto_branching,
                         overwrite = overwrite)

    def write(self, 
              exist_ok: bool =False) -> None:
        if self.path.exists and not exist_ok:
            raise FileExistsError
        self.path.mkdir(exist_ok=True)
    
        for node_name in self._content.keys():
            self._content[node_name].write()

    @staticmethod
    def read(path: Path) -> "StructuredDataset":
        # load all the files
        files = list(path.glob("*"))

        # leafs
        leafs = filter(lambda x: x.is_dir(), files)
        
        # data
        data = filter(lambda x: x.suffix  == ".npy", files)
        
        content = {}
        for leaf in leafs:
            content[leaf.name] = Leaf(path, 
                                      leaf.name,
                                      {})
            content[leaf.name].read()

        for data_node in data:
            content[data_node.stem] = Data(path,
                                           data_node.stem)

        return StructuredDataset(path.parent, path.stem, content)




class Data(Node):

    def __init__(self, 
                 parent_path: Path,
                 name: str) -> None:
        self._parent_path = parent_path  # type: Path
        self._name = name  # type: str
        self._data = None  # type: numpy.ndarray

        self._is_read = False  # type: bool
    
    @property
    def data(self) -> numpy.ndarray:
        return self._data
    
    @data.setter
    def data(self, data: numpy.ndarray) -> None:
        self._data = data
        self.is_read = True

    @property
    def is_read(self) -> bool:
        return self._is_read
    
    @is_read.setter
    def is_read(self, is_read: bool) -> None:
        self._is_read = is_read

    @property
    def name(self) -> str:
        return self._name

    @property
    def path(self) -> Path:
        return self._parent_path / "{:s}.npy".format(self.name)

    def write(self) -> None:
        if self.read:
            numpy.save(self.path, self._data)
    
    def read(self) -> numpy.ndarray:
        if not self.is_read:
            self._data = numpy.load(self.path)
        return self._data


