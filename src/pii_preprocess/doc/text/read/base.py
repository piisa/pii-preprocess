"""
Base class for reading text files
"""

import os

from typing import Dict, TextIO

from pii_data.helper.io import openfile
from pii_data.types.document import TYPE_META

from ...utils import add_default_meta


class BaseReader:
    """
    Abstract base class
    """

    def __init__(self, chunk_options: Dict = None, metadata: TYPE_META = None,
                 **kwargs):
        self.opt = chunk_options
        self.meta = metadata or {}
        self.kwargs = kwargs


    def base_read(self, inputfile: str, encoding: str = 'utf-8') -> TextIO:
        """
        Prepare & open a local text file
        """
        mtime = os.stat(inputfile).st_mtime
        add_default_meta(self.meta, origin="text", date=mtime)
        return openfile(inputfile, encoding=encoding)


    def read(self, inputfile: str, encoding: str = 'utf-8') -> str:
        """
        Read a local text file
        """
        with self.base_read(inputfile, encoding=encoding) as f:
            return f.read()
