"""
Read a text document and split it by word chunks.
"""

import re

from typing import Dict, Iterator

from pii_data.types.localdoc import SequenceLocalSrcDocument

from ...utils import chunker
from ..defs import DEFAULT_MAX_WORDS
from .base import BaseReader


class WordSplitter:
    """
    Split a document into chunks having at most "max_words" each, splitting
    words by whitespace
    """

    def __init__(self, doc: str, chunk_options: Dict):
        """
         :param chunk_options: max_words = maximum number of words in a chunk
        """
        self.doc = doc
        self.regex = re.compile(r"(\W+)")
        # multiply by 2 max_size, since we have a word + whitespace pair at
        # each split
        self.size = chunk_options.get("max_words", DEFAULT_MAX_WORDS)*2

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
