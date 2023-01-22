"""
Define a loader class that can load a local file in a number of formats as
an SrcDocument, by dispatching to an appropriate loader
"""
from pathlib import Path

from typing import Dict, Union, TextIO

from pii_data.helper.exception import ProcException, InvalidDocument
from pii_data.helper.misc import import_object
from pii_data.helper.config import TYPE_CONFIG_LIST
from pii_data.types.doc import SrcDocument

from .utils import get_loader_config
from .base import BaseLoader


class BaseDocumentLoader(BaseLoader):
    """
    A base class instantiated with an already loaded config
    """

    def __init__(self, config: Dict, debug: bool = False):
        """
          :param config: the loader configuration to use
          :param debug: print debug information
        """
        super().__init__(debug=debug)
        self.add_config(config)


    def load(self, src: Union[str, Path, TextIO], metadata: Dict = None,
             srcname: str = None) -> SrcDocument:
        """
        Load a source document by finding the appropriate loader class and
        instantiating it
          :param src: source to read the data from (it could be a filename
             or a file-like object)
          :param metadata: optional document-level metadata to add
          :param srcname: filename for the source (used when `src` is not
             a name)
        """
        err = []
        if not srcname:
            srcname = str(src)

        # Search all the mime types for this extension
        for loader in self.get_loaders(srcname):

            if loader.get("type") == "collection":
                raise ProcException("invalid loader for doc '{}': collection")

            # Import the loader class
            cls = import_object(loader["class"])
            kwargs = loader.get("class_kwargs", {})
            meta = kwargs.pop("metadata", {})
            if metadata:
                meta.update(metadata)

            # Instantiate the class
            try:
                return cls(src, metadata=meta, **kwargs)
            except InvalidDocument as e:
                err.add(str(e))

        raise ProcException("cannot load document '{}': {}", srcname,
                            ",".join(err))


# -----------------------------------------------------------------------


class DocumentLoader(BaseDocumentLoader):
    """
    The full document loader class
    """

    def __init__(self, config: TYPE_CONFIG_LIST = None, debug: bool = False):
        """
         :param configfile: list of configurations to add on top of the
           default config
        """
        cfg = get_loader_config(config, debug=debug)
        super().__init__(cfg, debug=debug)


    def __repr__(self) -> str:
        num = len(self.conf.loader)
        return f"<DocumentLoader #{num}>"
