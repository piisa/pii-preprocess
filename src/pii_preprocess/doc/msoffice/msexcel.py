"""
Read Microsoft Excel files (xlsx)
"""

from datetime import datetime
from collections.abc import Iterable

from openpyxl import load_workbook
from openpyxl.cell import Cell, ReadOnlyCell

from typing import List, Dict, Iterator, Union

from pii_data.helper.exception import UnimplementedException
from pii_data.types.doc.document import TYPE_META
from pii_data.types.doc.localdoc import TableLocalSrcDocument
from pii_data.dump.utils import ChunkIterWrapper


TYPE_CELL = Union[Cell, ReadOnlyCell]
TYPE_ROW_SRC = Iterable[TYPE_CELL]
TYPE_ROW_DST = Dict


def column_names(row: TYPE_ROW_SRC) -> List[str]:
    """
    Get the row with column names and return them
    """
    return [c.value for c in row]


class WorksheetIterable:
    """
    Iterate over the rows of a worksheet
    """

    def __init__(self, rows: Iterable[TYPE_ROW_SRC],
                 header: bool = True, context: bool = True):
        """
          :param rows: an iterable over the worksheet rows
          :param header: consider the first row as holding column names
          :param context: when iterating, add a context field to each cell
        """
        self.rows = rows
        self.context = context
        if header:
            self.colnames = column_names(next(rows))
            self.start = 2
        else:
            self.colnames = None
            self.start = 1


    def __iter__(self) -> Iterable[TYPE_ROW_DST]:
        """
        Return an iterable yielding the rows in the worksheet.
        Each row is a dict containind "id" and "data"
        """
        for r, row in enumerate(self.rows, start=self.start):
            yield {
                "id": r,
                #"data": self.row(row, r)
                "data": ChunkIterWrapper(self.row(row, r))
            }


    def row(self, row: TYPE_ROW_SRC, row_idx: int) -> TYPE_ROW_DST:
        """
        Return all cells from a row, as an iterable of dicts
        """
        for c, cell in enumerate(row, start=1):
            # Cell contents
            data = {
                "id": cell.coordinate,
                "data": cell.value,
            }
            # Add cell context: row id, column position and, if possible,
            # column name
            if self.context:
                data["context"] = {
                    "column": {"number": c},
                    "row": row_idx
                }
                if self.colnames:
                    data["context"]["column"]["name"] = self.colnames[c-1]
            # Return the cell
            yield data


# ------------------------------------------------------------------------


class _BaseExcelDocument:

    def _open(self, filename: str, rw: bool = False) -> TYPE_META:
        """
        Open an MS Excel file and load it
          :param filename: Excel filename to read
          :param rw: open for read/write (default is read-only)
          :return: the document general metadata
        """
        # Open the Excel file
        self.name = filename
        self.wb = load_workbook(filename=filename, read_only=not rw)
        #print(self.doc.sections)
        #print(self.doc.settings)

        # Read document generic metadata
        docinfo = {"origin": "msexcel", "type": "table"}
        for n in ("title", "creator", "subject", "modified"):
            v = getattr(self.wb.properties, n, None)
            if n == "creator":
                n = "author"
            if not v:
                continue
            if n != "modified":
                docinfo[n] = v.replace("\n", " ")
            else:
                docinfo["date"] = v.isoformat() if isinstance(v, datetime) else str(v)

        return {"document": docinfo}



class TableExcelDocument(TableLocalSrcDocument, _BaseExcelDocument):
    """
    Read one sheet of an Excel document into a TableSrcDocument
    """

    def __init__(self, filename: str, wsindex: int = 0, header: bool = True,
                 metadata: TYPE_META = None, iter_options: Dict = None,
                 **kwargs):
        """
          :param filename: name of the Excel file to open
          :param wsindex: index of worksheet to load
          :param header: the first row contains the column names
          :param metadata: additional metadata to add to the document description
          :param iter_options: options to pass to the cell iterator
             (default is to iterate with context)
        """
        if not iter_options:
            iter_options = {"context": True}
        docmeta = self._open(filename, "tree")
        super().__init__(metadata=docmeta, iter_options=iter_options, **kwargs)
        shname = self.wb.sheetnames[wsindex]
        if shname:
            self.add_metadata(document={'sheetname': shname})
        self.header = header
        if header:
            row = self.wb.worksheets[wsindex][1]
            self.add_metadata(column={'name': column_names(row)})
        if metadata:
            self.add_metadata(**metadata)


    def iter_base(self) -> Iterable[Dict]:
        """
        The base iterator, producing rows
        """
        ctx = self._iter_options.get("context")
        return WorksheetIterable(self.wb.worksheets[0].rows,
                                 self.header, context=ctx)


    def iter_full(self, context: bool = None) -> Iterable[Dict]:
        """
        The full iterator, producing cells
        """
        for row in self.iter_base():
            for cell in row["data"]:
                yield cell



class ExcelDocumentCollection:
    """
    Read all worksheets in an Excel file as a documento collection
    """

    def __init__(self, filename: str, metadata: TYPE_META = None, **kwargs):
        raise UnimplementedException("multiple sheets cannot be handled: {}",
                                     filename)


class ExcelDocument:
    """
    Wrapper to read an Excel file either as a single document (reading the
    first worksheet) or as a document collection
    """

    def __new__(self, filename: str, single: bool = True, **kwargs):
        """
         :param filename: Word file to read
         :param single: read only the first worksheet
        """
        if single:
            return TableExcelDocument(filename, **kwargs)
        else:
            return ExcelDocumentCollection(filename, **kwargs)
