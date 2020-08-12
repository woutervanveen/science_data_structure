import numpy
from pathlib import Path
from structures import Leaf, Node
from meta import Meta


class LeafNumpy(Leaf):

    def __init__(self,
                 parent: Node,
                 name: str,
                 meta: Meta) -> None:
        super().__init__(parent,
                         name,
                         meta)
        self._data = None  # type: numpy.ndarray
        self._is_read = False

    def read(self) -> numpy.ndarray:
        self._data = numpy.load(self.path / "data.npy")
        self._is_read = True

    def _get_data(self):
        if not self._is_read:
            self.read()
        return self._data

    def _set_data(self, data: numpy.ndarray) -> None:
        self._data = data

    def remove(self) -> None:
        (self.path / "data.npy").unlink()
        self.meta.path.unlink()
        self.path.rmdir()

    def _write_child(self) -> None:
        numpy.save(self.path / "data.npy", self._data)


available_formats = {
    "npy": LeafNumpy,
}
available_types = {
    numpy.ndarray: LeafNumpy
}

