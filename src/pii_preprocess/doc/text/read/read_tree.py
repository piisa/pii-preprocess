"""
Read a text document and create a tree by using indent
"""

from typing import TextIO, Iterable

from pii_data.helper.exception import InvalidDocument
from pii_data.types.localdoc import (BaseLocalSrcDocument, TreeLocalSrcDocument,
                                     SequenceLocalSrcDocument)

from ..defs import DEFAULT_INDENT
from .base import BaseReader


def add_blank(src: Iterable[str]) -> Iterable[str]:
    """
    Iterate over lines, adding empty lines to the previous one
    """
    prev = ''
    for line in src:
        if line.isspace():
            prev += line
            continue
        if prev:
            yield prev
        prev = line

    if prev:
        yield prev


class TreeReader(BaseReader):
    """
    Convert a plain text file to a data structure for a YAML PII Source
    Document, reading the file line by line.
    If instructed to do so, it can infer hierarchy from leading indent, and
    thus create a tree source document.
    """

    def __init__(self, indent: int, **kwargs):
        super().__init__(**kwargs)
        self.ind = int(indent) if indent is not None else DEFAULT_INDENT


    def read_tree(self, src: TextIO) -> BaseLocalSrcDocument:
        """
        Read chunks from the file and build a data stack tree
        """
        chunkid = 0
        currlev = 0
        maxlev = 0
        base = {"chunks": []}
        stack = [base]
        for line in add_blank(src):

            # Read the line, compute hierarchy level from indent
            raw = line.lstrip()
            lev = (len(line) - len(raw))//self.ind if self.ind else 0

            # Create the chunk
            chunkid += 1
            chunk = dict(id=str(chunkid), data=raw)

            # Find the place where to add the chunk
            if lev < currlev:
                stack = stack[:-1]
            elif lev > currlev:
                top = stack[-1]["chunks"][-1]
                top["chunks"] = []
                stack.append(top)

            # Add it
            stack[-1]["chunks"].append(chunk)
            currlev = lev
            maxlev = max(maxlev, currlev)

        # Create the document and return it
        cls = TreeLocalSrcDocument if maxlev else SequenceLocalSrcDocument
        return cls(chunks=base["chunks"], metadata=self.meta, **self.kwargs)


    def read(self, inputfile: str,
             encoding: str = 'utf-8') -> BaseLocalSrcDocument:
        """
        Open a raw text file and read it as a PII Source Document
        """
        with self.base_read(inputfile, encoding=encoding) as f:
            try:
                return self.read_tree(f)
            except Exception as e:
                raise InvalidDocument(f"invalid text document '{inputfile}': {e}") from e
