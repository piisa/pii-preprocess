# -*- coding: utf-8 -*
"""
Read a text document and split it by paragraphs, using punctuation, also with
options to limit paragraph sizes.
"""

from pii_data.types.doc.localdoc import SequenceLocalSrcDocument

from pii_preprocess.helper import ParagraphSplitter
from .base import BaseReader


class ParagraphReader(BaseReader):
    """
    Read a text file creating a chunk per line
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.splitter = ParagraphSplitter(separator=self.opt.get("separator"),
                                          min_words=self.opt.get("min_words"),
                                          max_words=self.opt.get("max_words"))


    def read(self, inputfile: str,
             encoding: str = 'utf-8') -> SequenceLocalSrcDocument:
        """
        Read a local text file
        """
        # Read document
        doc = super().read(inputfile, encoding)

        # Create a paragraph splitter from it
        paragraphs = self.splitter(doc)

        # Instantiate all chunks so that it can be iterated repeatedly
        chunks = list(paragraphs)

        # Return the SrcDocument object
        return SequenceLocalSrcDocument(chunks=chunks, metadata=self.meta,
                                        **self.kwargs)
