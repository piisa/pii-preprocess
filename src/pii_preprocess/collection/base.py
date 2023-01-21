"""
Define a base class to implement document collections

A subclass needs to implement an `iter_doc()` method
"""

from pathlib import Path

from typing import Iterable, Dict

from pii_data.helper.exception import UnimplementedException
from pii_data.helper.config import load_single_config, TYPE_CONFIG_LIST
from pii_data.types.doc import SrcDocument

from .. import defs
from ..loader.loader import BaseDocumentLoader


class DocumentCollection:
    """
    The base class for all document collections
    """

    def __init__(self, config: TYPE_CONFIG_LIST = None, metadata: Dict = None,
                 loader: BaseDocumentLoader = None, debug: bool = False,
                 skip_config_loading: bool = False):
        """
          :param config: loader config
          :param metadata: metadata to add to all loaded documents
          :param loader: a loader to use to load documents in the folder
            (if not passed, a new loader object will be instantiated)
          :param debug: activate debug output
          :param skip_config_loading: do not perform a full config load;
            just use the passed config
        """
        self.meta = metadata

        if skip_config_loading:
            self.config = config
        else:
            base = Path(__file__).parents[1] / "resources" / defs.DEFAULT_CONFIG_LOADER
            self.config = load_single_config(base, defs.FMT_CONFIG_LOADER, config)

        # Create a document loader
        self.loader = None if loader is False else \
            loader or BaseDocumentLoader(self.config, debug)


    def __repr__(self) -> str:
        return "<DocumentCollection>"


    def __iter__(self) -> Iterable[SrcDocument]:
        """
        Iterate over the documents in the collection
        """
        for doc in self.iter_doc():
            if self.meta:
                doc.add_metadata(dataset=self._meta)
            yield doc


    def iter_doc(self) -> Iterable[SrcDocument]:
        raise UnimplementedException("abstract class")
