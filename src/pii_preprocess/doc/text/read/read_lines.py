"""
Read a text document and split it by lines
"""

import re

from typing import Dict, Iterator

from pii_data.types.localdoc import SequenceLocalSrcDocument

from ...utils import chunker
from .base import BaseReader


# A newline, possibly followed by blank lines
NEWLINE = r"( \s*\n (?:\s*\n)* )"


class LineSplitter:

    def __init__(self, doc: str, chunk_options: Dict = None):
        self.doc = doc
        #self.size = chunk_options.get("min_words")
        self.regex = re.compile(NEWLINE, flags=re.X)

    def __iter__(self) -> Iterator[str]:
        return chunker(self.regex.split(self.doc), 2, smin=2)


class LineReader(BaseReader):
    """
    Read a text file creating a chunk per line
    """

    def read(self, inputfile: str,
             encoding: str = 'utf-8') -> SequenceLocalSrcDocument:
        """
        Read a local text file
        """
        doc = super().read(inputfile, encoding)
        chunks = LineSplitter(doc)
        return SequenceLocalSrcDocument(chunks=chunks, metadata=self.meta,
                                        **self.kwargs)
