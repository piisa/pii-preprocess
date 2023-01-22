"""
Load a local folder as a document collection
"""

from pathlib import Path

from typing import Iterable

from pii_data.helper.exception import InvArgException
from pii_data.types.doc import SrcDocument

from ..base import DocumentCollection


class FolderDocumentCollection(DocumentCollection):

    def __init__(self, folder: str, glob: str = None, recursive: bool = False,
                 **kwargs):
        """
          :param folder: base folder to use
          :param glob: a globbing pattern to select the files to load from the
             folder
          :param recursive: traverse all subdirectories

        The rest of arguments are used by the base class
        """
        super().__init__(**kwargs)

        self._recursive = recursive
        self._glob = glob
        self._base = Path(folder)
        if not self._base.is_dir():
            raise InvArgException("invalid folder: {}", self._base)


    def __repr__(self) -> str:
        return f"<FolderDocumentCollection: {self._base.stem}>"


    def _iter_recursive(self, base: Path):
        """
        Read a directory recursively, with no globbing
        """
        for elem in base.iterdir():
            if elem.is_file():
                yield elem
            elif elem.is_dir():
                yield from self._iter_recursive(elem)


    def _iter_simple(self, base: Path):
        """
        Read a directory in a single pass (either non-recursive, or recursive
        with globbing) using Pathlib iterators
        """
        # Create the iterator
        it = base.iterdir() if not self._glob else \
            base.glob(self._glob) if not self._recursive else \
            base.rglob(self._glob)
        # Traverse it
        for elem in it:
            if elem.is_file():
                yield elem


    def iter_doc(self) -> Iterable[SrcDocument]:
        """
        Iteration main entry point
        """
        # Decide which method we'll use
        it = self._iter_recursive if self._recursive and not self._glob \
            else self._iter_simple
        # Traverse
        for elem in it(self._base):
            yield self.loader.load(elem)
