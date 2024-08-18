"""
Save document collections locally
"""

from pathlib import Path

from pii_data.helper.exception import InvArgException
from pii_data.helper.io import openuri
from pii_data.types.doc import SrcDocument
from pii_data.types.doc.localdoc import dump_file


class CollectionSaver:
    """
    A class to save a collection of documents.
    It can be used as a context manager
    """

    def __init__(self, name: str, format: str, indent: int = None):
        """
         :param name: output name
         :param format: output format (json, yaml, txt or jsonl)
         :param indent: document indentation, for JSON & Text output

        For JSON-L format, the output will be a single file; else
        the output name must be a directory
        """
        self.indent = indent
        self.fmt = format
        self._base = Path(name)
        self._out = None
        if self.fmt in ("ndjson", "jsonl"):
            self._out = openuri(name, "wt")
        elif not self._base.is_dir():
            raise InvArgException("invalid output '{}': is a file", self._base)
        self.num = 1


    def save(self, doc: SrcDocument):
        """
        Save a document
        """
        if self._out:
            # JSONL
            dump_file(doc, self._out, "json", indent=False)
            print(file=self._out)        # a newline
        else:
            # Other formars: save in a folder
            safename = doc.id.replace("/", "-")
            outname = self._base / f"{self.num:03}-{safename}"
            if not outname.suffix:
                outname = outname.with_suffix("." + self.fmt)
            dump_file(doc, outname, self.fmt, indent=self.indent)
        self.num += 1


    def close(self):
        """
        Close output. Relevant for single-file (e.g. JSON-L) output
        """
        if self._out:
            self._out.close()


    def __enter__(self):
        return self


    def __exit__(self, *args):
        self.close()
