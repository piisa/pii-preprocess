"""
Define a loader class that can load a local fila in a numberformats as 
an SrcDocument, by dispatching to an appropriate loader
"""

from importlib.resources import open_text
from collections import defaultdict
from pathlib import Path
import json

from typing import Dict, TextIO, List

from pii_data.helper.exception import ProcException, InvalidDocument
from pii_data.helper.io import base_extension
from pii_data.helper.misc import import_object
from pii_data.types import SrcDocument


DEFAULT_CONFIG = "doc-loader.json"


def open_resource(name: str) -> TextIO:
    """
    Open a text resource file
    """
    return open_text("pii_preprocess.resources", name)


class DocumentLoader:

    def __init__(self, configfile: List[str] = None):
        """
         :param configfile| list of configuration files to add on top of the
           default config
        """
        self.types = defaultdict(list)
        self.loaders = {}

        # Load default configuration
        self.add_config(json.load(open_resource(DEFAULT_CONFIG)))

        # Add additional config files
        if configfile:
            if isinstance(configfile, (str, Path)):
                configfile = [configfile]
            for f in configfile:
                self.read_config(f)


    def __repr__(self) -> str:
        return f"<DocumentLoader {len(self.loaders)}>"


    def add_config(self, config: Dict):
        """
        Add a configuration dictionary to the object
        """
        self.loaders.update(config.get("loaders", {}))
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


    def read_config(self, configname: str):
        """
        Read a configuration file and add it to the object
        """
        with open(configname, encoding="utf-8") as f:
            try:
                self.add_config(json.load(f))
            except json.JSONDecodeError as e:
                raise ProcException("Invalid config file {}: {}", configname, e)


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
