"""
Read a text document and split it by word chunks.
"""

import re

from typing import Dict, Iterator

from pii_data.types.localdoc import SequenceLocalSrcDocument

from ..defs import DEFAULT_MAX_WORDS
from ..utils import chunker
from .base import BaseReader


class WordSplitter:

    def __init__(self, doc: str, chunk_options: Dict):
        self.doc = doc
        self.size = chunk_options.get("max_words", DEFAULT_MAX_WORDS)*2
        self.regex = re.compile(r"(\W+)")

    def __iter__(self) -> Iterator[str]:
        return chunker(self.regex.split(self.doc), self.size)


class WordsReader(BaseReader):
    """
    Read a text file creating chunks as groups of words using whitespace as
    word separator
    """

    def read(self, inputfile: str,
             encoding: str = 'utf-8') -> SequenceLocalSrcDocument:
        """
        Read a local text file
        """
        doc = super().read(inputfile, encoding)
        chunks = WordSplitter(doc, self.opt)
        return SequenceLocalSrcDocument(chunks=chunks, metadata=self.meta,
                                        **self.kwargs)
