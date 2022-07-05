"""
Read a CSV file into a PII tabular source document
"""

import csv
from itertools import islice
from types import MappingProxyType

from typing import Dict, Iterable, List, TextIO

from pii_data.helper.exception import ProcException
from pii_data.types import SrcDocument
from pii_data.types.localdoc import TabularLocalSrcDocument


# Default number of rows per chunk
DEFAULT_CHUNK_SIZE = 512


class CsvDocument(SrcDocument):
    """
    A source document class that can read CSV data
    """

    def __init__(self, document_header: Dict = None,
                 add_chunk_context: bool = False,
                 csv_options: Dict = None,
                 csv_header: bool = True,
                 chunk_size: int = DEFAULT_CHUNK_SIZE):
        """
          :param document_header:
          :param add_chunk_context: add context info when iterating over chunks
          :param csv_options: options to pass to the Python CSV reader
          :param csv_header: if the first row is a header row with column names
          :param chunk_size: how many rows to pack into one chunk
        """
        if document_header is None:
            document_header = {}
        document_header["type"] = "tabular"
        super().__init__(document_header, add_chunk_context)
        self._csv_options = csv_options
        self._csv_header = bool(csv_header)
        self._chunk_size = chunk_size
        self._r = None


    def __repr__(self) -> str:
        return "<CsvDocument>"


    def open(self, source: TextIO, csv_options: Dict = None,
             csv_header: bool = None) -> Dict:
        """
         :param source: a data source, should contain text CSV rows
         :param csv_options: override the general argument in the constructor
         :param csv_header: override the general argument in the constructor
        """
        # Set options from arguments or or defaults
        if csv_options is None:
            csv_options = self._csv_options
        if csv_header is None:
            csv_header = self._csv_header

        # Open file
        self._r = csv.reader(source, **(csv_options or {}))

        # read the header row and add to context
        if csv_header:
            self.add_metadata(column={'name': list(next(self._r))})


    def get_chunks(self) -> Iterable[List]:
        """
        Get an iterable over document chunks (which will be chunks of document
        rows)
        """
        if not self._r:
            raise ProcException('unopened tabular source')

        while True:
            chunk = list(islice(self._r, self._chunk_size))
            if not chunk:
                break
            yield chunk


# -----------------------------------------------------------------------------

class LocalCsvDocument(CsvDocument, TabularLocalSrcDocument):
    """
    An object to read a local CSV file
    """

    def __init__(self, filename: str, id_path_prefix: str = None, **kwargs):
        """
         :param filename: CSV filename to open
         :param id_path_prefix: path prefix to remove from the document id
           If `False`, the filename will not be used for the document id (a
           random UUID will be generated instead)
        """
        super().__init__(**kwargs)
        self.open(filename, id_path_prefix)


    def __repr__(self) -> str:
        name = getattr(self._f, 'name', '<>') if self._f else None
        return f"<CsvDocument {name}>"


    def open(self, inputfile: str, id_path_prefix: str = None) -> Dict:
        """
        Open a local CSV file
        """
        self._f = open(inputfile, encoding='utf-8')
        super().open(self._f)
        if id_path_prefix is not False:
            self.set_id_path(inputfile, id_path_prefix)


    def close(self):
        """
        Close the CSV file
        """
        if self._f:
            self._f.close()
            self._f = None


    def __enter__(self):
        return self


    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.close()
