"""
Define a loader class wrapper that can load either an individual document file
or a  collection of documents, with a unified interface.
"""

from pii_data.helper.exception import ProcException, InvalidDocument
from pii_data.helper.misc import import_object
from pii_data.helper.config import TYPE_CONFIG_LIST
from pii_data.types.doc import SrcDocument

from typing import Iterable, Dict

from .base import BaseLoader
from .utils import get_loader_config



class LoaderWrapper(BaseLoader):
    """
    Load documents & collections
    """

    def __init__(self, config: TYPE_CONFIG_LIST = None, debug: bool = False):
        """
         :param config: list of configurations to add on top of the
           default configs
        """
        super().__init__(debug=debug)
        self.raw_config = get_loader_config(config, debug=debug)
        self.add_config(self.raw_config)


    def __repr__(self) -> str:
        return f"<LoaderWrapper #{len(self.conf.loader)}>"


    def load(self, name: str, metadata: Dict = None) -> Iterable[SrcDocument]:
        """
        Load a source document or a collection of them, by finding the
        appropriate loader class and instantiating it
          :param name: name if the document or collection to load
          :param metadata: optional document-level metadata to add
        """
        err = []
        n = 0

        # Search all possible loaders for this source
        for n, loader in enumerate(self.get_loaders(name), start=1):

            # Import the loader class
            cls = import_object(loader["class"])
            kwargs = loader.get("class_kwargs", {})
            meta = kwargs.pop("metadata", {})
            if metadata:
                meta.update(metadata)

            # Instantiate the class and produce the documents
            try:
                if loader.get("type") == "collection":
                    # a collection loader
                    obj = cls(name, config=self.raw_config, metadata=meta,
                              skip_config_loading=True, **kwargs)
                    yield from obj
                else:
                    # a document loader
                    yield cls(name, metadata=meta, **kwargs)
                return

            except InvalidDocument as e:
                err.add(str(e))

        raise ProcException("cannot load source '{}': {}", name,
                            "no loader" if n == 0 else ",".join(err))
