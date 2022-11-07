# -*- coding: utf-8 -*
"""
Read a text document and split it by paragraphs, using punctuation, also with
options to limit paragraph sizes.
"""
import re

from typing import Dict, Iterator

from pii_data.types.localdoc import SequenceLocalSrcDocument

from ...utils import chunker
from .base import BaseReader


# End of sentence punctuation for Latin, Devanagari, Chinese & Arabic scripts
EOS = r"[\.\?!।|。！？⋯…؟]+"

# End of paragraph marked by blank lines
EOP_BLK = r"\n (?:\s*\n){1,}"

# EOP by either:
#  - EOS followed by optional whitespace and at least a newline
#  - an empty line
EOP_EOS = r"(?:" + EOS + r"\s*\n (?:\s*\n)* | \n (?:\s*\n){1,} )"



class ParagraphSplitter:
    """
    Take a string buffer and create an iterator by paragraphs
    """

    def __init__(self, doc: str, chunk_options: Dict):
        """
          :param doc: document to split, as a single string
          :param chunk_options: chunking options
             - min_words: minimum number of words in a paragraph, if less join
               with the next paragraph, if 0 (default) there is no minimum
             - max_words: maximum number of words in a paragraph, if greater
               split paragraph, if 0 (default) there is no maximum
        """
        self.doc = doc
        # Main regular expression
        eos = chunk_options.get("eos", False)
        self.reg = re.compile(r"(" + (EOP_EOS if eos else EOP_BLK) + r")",
                              flags=re.X)
        # Word limits
        self.wmin = int(chunk_options.get("min_words", 0))
        self.wmax = int(chunk_options.get("max_words", 0))
        if self.wmin or self.wmax:
            self.ws = re.compile(r"(\W+)")


    def __iter__(self) -> Iterator[str]:
        """
        Iterator over paragraphs, possibly with word limits
        """
        # If there are no word limits, just iterate over paragraphs
        if not self.wmin and not self.wmax:
            for para in chunker(self.reg.split(self.doc), 2):
                if para:
                    yield para
            return

        # Iteration with word limits
        prev = ""
        prev_nw = 0
        for para in chunker(self.reg.split(self.doc), 2):

            # Split paragraph into words (chunks of word+ws), and count them
            words = list(chunker(self.ws.split(para), 2, 2))
            para_nw = len(words)

            # If there is minimum and we don't reach it, continue iterating
            if self.wmin and prev_nw + para_nw <= self.wmin:
                prev += para
                prev_nw += para_nw
                continue

            if not self.wmax or prev_nw + para_nw < self.wmax:

                # If there is no maximum, or we are below it, produce a chunk
                yield prev + para

            else:

                # Here we are above the maximum
                if prev:
                    yield prev  # release previous chunk buffer

                if para_nw < self.wmax:
                    yield para  # the currrent chunk is below max
                else:
                    # the chunk is above max, split it
                    for i in range(0, len(words), self.wmax):
                        yield "".join(words[i:i+self.wmax])

            # Reset
            prev = ""
            prev_nw = 0

        # Last chunk, if present
        if prev:
            yield prev


class ParagraphReader(BaseReader):
    """
    Read a text file creating a chunk per line
    """

    def read(self, inputfile: str,
             encoding: str = 'utf-8') -> SequenceLocalSrcDocument:
        """
        Read a local text file
        """
        # Read document and create a paragraph splitter from it
        doc = super().read(inputfile, encoding)
        chunks = ParagraphSplitter(doc, self.opt)

        # Return the SrcDocument object
        return SequenceLocalSrcDocument(chunks=chunks, metadata=self.meta,
                                        **self.kwargs)
