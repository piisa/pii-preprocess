"""
Read raw text documents
"""

from typing import Dict

from pii_data.helper.exception import InvArgException
from pii_data.types.localdoc import BaseLocalSrcDocument

from .read import SingleReader, LineReader, ParagraphReader, WordsReader, TreeReader


# -----------------------------------------------------------------------


def load_text(inputfile: str, chunk_options: Dict,
              **kwargs) -> BaseLocalSrcDocument:
    """
    Read a local raw text file and convert it to PII Source Document
     :param inputfule: name of the filename to read
     :param chunk_options: options for document chunking
     :param kwargs: arguments passed to the SrcDocument subclass constructor
        (e.g. iter_options, metadata)

    The basic chunk option is "mode", which defines how the text file will be
    decomposed in chunks:
      * "single": the whole document in a single chunk
      * "line": each line is one chunk
      * "tree": indentation is used to define a document hierarchy
      * "paragraph": document is split into paragraphs
      * "words": document is split into chunks of whole words
    """
    # Instantiate the right object
    mode = chunk_options.get('mode', 'line')
    if mode == "single":
        reader = SingleReader(**kwargs)
    elif mode == "line":
        reader = LineReader(**kwargs)
    elif mode == 'tree':
        indent = chunk_options.get("indent")
        reader = TreeReader(indent, **kwargs)
    elif mode in ("para", "paragraph"):
        reader = ParagraphReader(chunk_options=chunk_options, **kwargs)
    elif mode == "word":
        reader = WordsReader(chunk_options=chunk_options, **kwargs)
    else:
        raise InvArgException(f"unknown mode {mode}")

    # Read the file
    return reader.read(inputfile)


class TextSrcDocument:
    """
    Read a text file and create a SrcDocument from it
    """

    def __new__(self, inputfile: str, chunk_options: Dict = None,
                **kwargs) -> BaseLocalSrcDocument:
        """
         :param inputfile: name of the filename to read
         :chunk_options: options for document chunking
         :param kwargs: arguments passed to the SrcDocument subclass constructor
           (e.g. iter_options, metadata)
        """
        return load_text(inputfile, chunk_options or {}, **kwargs)
