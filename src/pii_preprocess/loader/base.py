"""
The base class to implement document & collection loaders
"""

import re
from pathlib import Path
from types import SimpleNamespace
from collections import defaultdict

from typing import Dict, Iterable

from pii_data.defs import FMT_CONFIG_PREFIX
from pii_data.helper.exception import ProcException, ConfigException
from pii_data.helper.io import base_extension
from pii_data.helper.logger import PiiLogger

from .. import defs


# ------------------------------------------------------------------------


class BaseLoader:
    """
    A base class for a loader object
    """

    def __init__(self, debug: bool = False):
        self.debug = debug
        self.log = PiiLogger(__name__, debug=debug)
        self.conf = SimpleNamespace(extension=defaultdict(list),
                                    pattern=[], loader={})


    def add_config(self, config: Dict):
        """
        Add a configuration dictionary to the object
          :param config: a configuration section corresponding to a loader
            config
        """
        fmt = config.get("format")
        if fmt != FMT_CONFIG_PREFIX + defs.FMT_CONFIG_LOADER:
            raise ConfigException("invalid format for loader config data")

        # Add loaders
        loaders = config.get("loaders", {})
        for k, v in loaders.items():
            if v and "class" not in v:
                raise ProcException("invalid loader for '{}': no class", k)
        self.conf.loader.update(loaders)

        # Add document types
        pattern = []
        for elem in config.get("types", {}):

            # Check fields
            if "mime" not in elem:
                raise ProcException("invalid types config: no 'mime' field")
            if "ext" not in elem and "pattern" not in elem:
                raise ProcException("invalid types config: no 'ext' or 'pattern' field")
            if elem["mime"] not in self.conf.loader:
                raise ProcException("no mime loader for: {}", elem["mime"])

            # Add a regex pattern
            if "pattern" in elem:
                pat = {"regex": re.compile(elem["pattern"]), **elem}
                pattern.append(pat)
                continue

            # Add an extension
            extlist = elem["ext"]
            if isinstance(extlist, str):
                extlist = [extlist]
            for e in extlist:
                self.conf.extension[e].insert(0, elem["mime"])

        if pattern:
            self.conf.pattern = pattern[::-1] + self.conf.pattern


    def get_loaders(self, name: str) -> Iterable[Dict]:
        """
        Get all loaders applicable to a source
        """
        sname = str(name)
        ext = base_extension(sname)
        mime = []

        # Add types based on regex patterns
        for pattern in self.conf.pattern:
            if not pattern["regex"].match(sname):
                continue
            if "ext" in pattern and ext not in pattern["ext"]:
                continue
            mime.append(pattern["mime"])

        # Add types based on object type or file extension
        if Path(name).is_dir():
            mime.append("inode/directory")
        else:
            mime += self.conf.extension.get(ext, [])

        if not mime:
            raise ProcException("cannot find a mime type for file: {}", name)

        # Return the loaders for these mime types
        return filter(None, (self.conf.loader[m] for m in mime))
