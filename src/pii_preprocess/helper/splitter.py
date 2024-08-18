# -*- coding: utf-8 -*-
"""
A class to split a text buffer into chunks, delimited by either paragrapahs or
sentence separators
"""
from itertools import islice

import regex

from typing import Iterable, Iterator


# End of sentence punctuation for Latin, Devanagari, Chinese & Arabic scripts
EOS = r"[\.\?!।|。！？⋯…؟]+"

# EOP_BLK: End of paragraph marked by blank lines
EOP_BLK = r"\n (?:\s*\n){1,}"

# EOP_EOSN: EOP by either
#  - EOS followed by optional whitespace and at least a newline
#  - a blank line
EOP_EOSN = r"(?:" + EOS + r"\s*\n (?:\s*\n)* | \n (?:\s*\n){1,} )"

# EOP_EOS: EOP by either
#  - a "reduced" EOS mark (EOS except a period), plus optional quotes and/or ws
#  - a blank line
#  - an EOS sequence: sequence of letters ending in lowercase + period + ws
# (Note: the EOS sequence can produce false positives, eg. for abbreviations)
EOS_NODOT = r"[\?!।|。！？⋯…؟]+"
EOP_EOS = r'(?:' + EOS_NODOT + r'"?\s? | \n\s*\n | \w+ \p{Ll} [\)"]? \. "? \s+ )'


def chunker(it: Iterable[str], size: int, smin: int = 0) -> Iterable[str]:
    """
    Join an iterator into groups of consecutive chunks
     :param it: iterator to group
     :param size: number of items in each group
     :param smin: ignore groups smaller than this size
    """
    it = iter(it)
    while True:
        chunk = list(islice(it, size))
        if not chunk:
            return
        if not smin or len(chunk) >= smin:
            yield "".join(chunk)


class ParagraphSplitter:
    """
    Define an object that takes a string buffer and returns an iterator
    splitting the buffer by paragraphs
    """

    def __init__(self, separator: str = None, min_words: int = None,
                 max_words: int = None):
        """
         :param separator: "eop" (separate by paragraphs, delimited by blank
           lines, default), "eosn" (separate by end of sentence + newline), or
           "eos" (separate by end of sentence)
         :param min_words: minimum number of words in a paragraph, if less join
           with the next paragraph, if 0 (default) there is no minimum
         :param max_words: maximum number of words in a paragraph, if greater
           split paragraph, if 0 (default) there is no maximum
        """

        self.psep = separator or "eop"
        psep_regex = EOP_EOSN if self.psep == "eosn" else EOP_EOS if self.psep == "eos" else EOP_BLK

        # Main regular expression
        self.reg = regex.compile(rf"({psep_regex})", flags=regex.X)

        # Word limits
        self.wmin = int(min_words or 0)
        self.wmax = int(max_words or 0)
        if self.wmin or self.wmax:
            self.ws = regex.compile(r"(\W+)")


    def __repr__(self) -> str:
        return f"<ParagraphSplitter {self.psep}>"


    def __call__(self, doc: str) -> Iterator[str]:
        """
        Iterator over paragraphs, possibly with word limits
        """
        # If there are no word limits, just iterate over paragraphs
        if not self.wmin and not self.wmax:
            for para in chunker(self.reg.split(doc), 2):
                if para:
                    yield para
            return

        # Iteration with word limits
        prev = ""
        prev_nw = 0
        for para in chunker(self.reg.split(doc), 2):

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
