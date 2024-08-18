"""
Load a JSON-L aka NDJSON as a document collection.
Each line in the file is assumed to contain a serialized PIISA document
"""

import json
from pathlib import Path

from typing import Dict, Iterable

from pii_data.helper.exception import InvArgException, InvalidDocument
from pii_data.helper.io import openfile
from pii_data.types.doc.localdoc import check_document_format, create_document_object
from pii_data.types.doc import SrcDocument

from ..base import DocumentCollection



class JsonlDocumentCollection(DocumentCollection):

    def __init__(self, path: str, config: Dict = None,
                 encoding: str = None, ignore_errors: bool = False, **kwargs):
        """
         :param config:
         :param encoding: charset encoding in the JSON-L file
         :param ignore_errors: ignore lines with parsing/formatting errors

        All other arguments are sent to the parent class
        """
        super().__init__(config=config, loader=False, **kwargs)

        self._encoding = encoding
        self._ignore_errors = ignore_errors
        self._path = Path(path)
        if not self._path.is_file():
            raise InvArgException("not a valid file: {}", self._path)


    def __repr__(self) -> str:
        return f"<JsonlDocumentCollection: {self._path.name}>"


    def iter_doc(self) -> Iterable[SrcDocument]:
        """
        Read the JSON-L file and iterate over its lines
        """
        with openfile(self._path, "rt", encoding=self._encoding) as f:
            for n, line in enumerate(f, start=1):

                try:
                    data = json.loads(line)
                except json.JSONDecodeError as e:
                    if self._ignore_errors:
                        continue
                    raise InvalidDocument(f"Error: {e}: {self._path}, line {n}")

                try:
                    check_document_format(data)
                    yield create_document_object(data)
                except InvalidDocument as e:
                    if self._ignore_errors:
                        continue
                    raise InvalidDocument(f"Error: {e}: {self._path}, line {n}")
