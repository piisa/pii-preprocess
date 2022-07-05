"""
Read a CSV file into a PII tabler source document
"""

import csv
from itertools import islice

from typing import Dict, Iterable, List, TextIO

from pii_data.helper.exception import ProcException
from pii_data.types.document import TableSrcDocument, TYPE_META
from pii_data.types.localdoc import TableLocalSrcDocument



class CsvDocument(TableSrcDocument):
    """
    A source document class that can read CSV data
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
        docmeta = {"document": {"type": "table", "origin": "csv"}}
        super().__init__(iter_options=iter_options, metadata=docmeta)
        if metadata:
            self.add_metadata(**metadata)
        self._csv_options = csv_options
        self._csv_header = bool(csv_header)
        self._r = None


    def __repr__(self) -> str:
        return "<CsvDocument>"


    def open(self, source: TextIO, csv_options: Dict = None,
             csv_header: bool = None) -> Dict:
        """
         :param source: a data source, which must produce CSV rows
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

        # Read the header row and add to context
        if csv_header:
            self.add_metadata(column={'name': list(next(self._r))})


    def iter_base(self) -> Iterable[List]:
        """
        Produce an iterable over document rows
        """
        if not self._r:
            raise ProcException('unopened CSV table source')

        for n, row in enumerate(self._r, start=1):
            yield {"id": f"R{n}", "data": row}


    def iter_base_block(self, block_size: int) -> Iterable[List]:
        """
        Get a base iterable grouping rows in blocks.
          :param block_size: number of rows to deliver at each iteration
        """
        if not self._r:
            raise ProcException('unopened table source')

        n = 1
        while True:
            chunk = list(islice(self._r, block_size))
            if not chunk:
                break
            yield {"id": f"B{n}", "data": chunk}
            n += 1


# -----------------------------------------------------------------------------

class LocalCsvDocument(CsvDocument, TableLocalSrcDocument):
    """
    A class to read a local CSV file
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
        return f"<CsvDocument file={name}>"


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
