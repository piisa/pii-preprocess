"""
Define a loader class that can load a local fila in a numberformats as 
an SrcDocument, by dispatching to an appropriate loader
"""

from collections import defaultdict
from pathlib import Path

from typing import Dict

from pii_data.helper.exception import ProcException, InvalidDocument
from pii_data.helper.io import base_extension
from pii_data.helper.misc import import_object
from pii_data.helper.config import load_single_config, TYPE_CONFIG_LIST
from pii_data.types.doc import SrcDocument

from .. import defs


DEFAULT_CONFIG = "doc-loader.json"



class DocumentLoader:

    def __init__(self, config: TYPE_CONFIG_LIST = None):
        """
         :param configfile: list of configuration files to add on top of the
           default config
        """
        self.types = defaultdict(list)
        self.loaders = {}

        # Load configuration
        base = Path(__file__).parents[1] / "resources" / DEFAULT_CONFIG
        config = load_single_config(base, defs.FMT_CONFIG_LOADER, config)
        self.add_config(config)


    def __repr__(self) -> str:
        return f"<DocumentLoader {len(self.loaders)}>"


    def add_config(self, config: Dict):
        """
        Add a configuration dictionary to the object
        """
        # Add loaders
        self.loaders.update(config.get("loaders", {}))

        # Add document types
        for elem in config.get("types", {}):
            # Check fields
            for f in ("ext", "mime"):
                if f not in elem:
                    raise ProcException("Invalid type config: no '{}' field", f)
            # Add the element
            extlist = elem["ext"]
            if isinstance(extlist, str):
                extlist = [extlist]
            for e in extlist:
                self.types[e].append(elem)


    def load(self, docname: str, metadata: Dict = None) -> SrcDocument:
        """
        Load a source document by finding the appropriate loader class and
        instantiating it
          :param docname: filename containing the document to load
          :param metadata: optional document-level metadata to add
        """
        ext = base_extension(docname)
        if ext not in self.types:
            raise ProcException("cannot find a type for file: {}", docname)
        err = []

        # Search all the mime types for this extension
        for elem in self.types[ext]:

            # Find the loader for this mime type
            mime = elem.get("mime")
            if mime not in self.loaders:
                raise ProcException("no loader available for type: {}", mime)
            loader = self.loaders[mime]
            if "class" not in loader:
                raise ProcException("invalid loader config for type: {}: no class", mime)
            # Import the loader class
            cls = import_object(loader["class"])
            kwargs = loader.get("class_kwargs", {})
            meta = kwargs.pop("metadata", {})
            if metadata:
                meta.update(metadata)

            # Instantiate the class
            try:
                return cls(docname, metadata=meta, **kwargs)
            except InvalidDocument as e:
                err.add(str(e))

        raise ProcException("cannot load document '{}': {}", docname,
                            ",".join(err))
