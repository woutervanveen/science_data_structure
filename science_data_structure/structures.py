import abc


class Node(abc.ABC):
    """
    Abstract class that forms the basic component
    of the structured data-set
    """
    @abc.abstractproperty
    def name(self) -> str:
        pass

    @abc.abstractproperty
    def path(self) -> str:
        pass

class Leaf(Node):

    def __init__(self) -> None:
        pass

    @property
    def name(self) -> str:
        pass

    @property
    def path(self) -> str:
        pass

class Data(Node):

    def __init__(self) -> None:
        pass

    @property
    def name(self) -> str:
        pass

    @property
    def path(self) -> str:
        pass


class StructuredDataset:
    """
    StructuredDataset
    """
    
    def __init__(self,
                 path: str) -> None:
        self._path = path


    @property
    def path(self) -> str:
        return self._path



