"""
Read a CSV file into a PII table source document
"""

import os
import csv
from itertools import islice
from collections import namedtuple
from types import SimpleNamespace

from typing import Dict, Iterable, List, TextIO, Iterator

from pii_data.helper.exception import UnimplementedException
from pii_data.helper.io import openfile
from pii_data.types.document import TableSrcDocument, TYPE_META
from pii_data.types.localdoc import TableLocalSrcDocument

from .utils import add_default_meta, as_bool


class CsvDocument(TableSrcDocument):
    """
    Am abstract source document class that can read CSV data.
    Subclasses need to implement the get_base_iter() method.
    They also need to make sure in their constructors that any pertinent info
    (e.g. column names) is pushed to document metadata upon leaving the
    constructor.
    """

    def __init__(self, iter_options: Dict = None,
                 csv_options: Dict = None,
                 csv_header: bool = True, metadata: TYPE_META = None):
        """
          :param iter_options: iteration options
          :param csv_options: options to pass to the Python CSV reader
          :param csv_header: if the first row is a header row with column names
          :param metadata: document-level metadata to add to the document
        """
        basemeta = {"document": {"type": "table", "origin": "csv"}}
        super().__init__(iter_options=iter_options, metadata=basemeta)
        if metadata:
            self.add_metadata(**metadata)
        self._opt = SimpleNamespace(csv_options=csv_options,
                                    csv_header=as_bool(csv_header))


    def __repr__(self) -> str:
        return "<CsvDocument>"


    def iter_base(self) -> Iterable[List]:
        """
        Produce an iterable over document rows
        """
        it = self.get_base_iter()
        for n, row in enumerate(it, start=1):
            yield {"id": f"R{n}", "data": row}


    def iter_base_block(self, block_size: int) -> Iterable[List]:
        """
        Get a base iterable grouping rows in blocks.
          :param block_size: number of rows to deliver at each iteration
        """
        it = self.get_base_iter()
        n = 1
        while True:
            chunk = list(islice(it, block_size))
            if not chunk:
                break
            yield {"id": f"B{n}", "data": chunk}
            n += 1


class TextIOCsvDocument(CsvDocument):
    """
    A slightly-less-abstract CSV document class.
    Subclasses need to provide the open() method, which should return a TextIO
    object from which the CSV raw text data can be fetched.
    The method is assumed to be re-entrant, i.e. a document can be reopened
    and iterated many times.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._open_data()       # ensure the CSV header is read


    def get_base_iter(self) -> Iterator[List]:
        """
        Return the base iterator
        """
        # Open (or reopen) source as needed
        if self._src is None or self._src.used:
            self._open_data()
        # Ste status & return iterator
        self._src.used = True
        return self._src.it


    def _open_data(self):
        """
        Open & prepare the source objects
        """
        # Open source and create a CSV reader around it
        f = self.open()
        it = csv.reader(f, **(self._opt.csv_options or {}))

        # Read the header row and add to metadata
        if self._opt.csv_header:
            colnames = list(next(it))
            self.add_metadata(column={'name': colnames})

        # Store objects
        self._src = SimpleNamespace(file=f, it=it, used=False)


    def open(self):
        raise UnimplementedException("abstract class TextIOCsvDocument")


    def close(self):
        if self._src:
            self._src.file.close()
            self._src = None


    def __enter__(self):
        return self


    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.close()


# -----------------------------------------------------------------------------

FileData = namedtuple("FILEDATA", "name id_path_prefix")


class LocalCsvDocument(TextIOCsvDocument, TableLocalSrcDocument):
    """
    A class to read a local CSV file
    """

    def __init__(self, filename: str, id_path_prefix: str = None,
                 metadata: TYPE_META = None, **kwargs):
        """
          :param filename: CSV filename to open
          :param id_path_prefix: set the id to the document filename, removing
            the prefix indicated
          :param metadata: metadata to add to the document

        if `id_path_prefix` is `False`, the filename will not be used for the
        document id. If the document metadata includes an id, it will be
        used, else a random UUID will be generated.
        """

        # Add the file timestamp to the metadata
        if not metadata:
            metadata = {}
        mtime = os.stat(filename).st_mtime
        add_default_meta(metadata, date=mtime)

        # Store file coordinates & initialize
        self._file = FileData(filename, id_path_prefix)
        super().__init__(metadata=metadata, **kwargs)


    def __repr__(self) -> str:
        return f"<CsvDocument file={self._file.name}>"


    def open(self) -> TextIO:
        """
        Open the local CSV file, as configured in the object
        """
        if self._file.id_path_prefix is not False:
            self.set_id_path(self._file.name, self._file.id_path_prefix)
        return openfile(self._file.name, encoding='utf-8')


    def csv_options(self, csv_options: Dict = None, csv_header: bool = None):
        """
        Override the default options
        """
        if csv_options is not None:
            self._opt.csv_options = csv_options
        if csv_header is not None:
            self._opt.csv_header = csv_header


    def openfile(self, inputfile: str, id_path_prefix: str = None) -> TextIO:
        """
        Expliclty open a local CSV file
        """
        self._file = FileData(inputfile, id_path_prefix)
        return self.open()
