

import json
from pathlib import Path

from typing import Dict, Iterable

from pii_data.helper.exception import InvArgException
from pii_data.helper.io import openfile
from pii_data.types.doc import SrcDocument

from ..base import DocumentCollection



class NDJsonDocumentCollection(DocumentCollection):

    def __init__(self, path: str, config: Dict = None,
                 metadata: Dict = None, encoding: str = None):
        super().__init__(config=config, loader=False, metadata=metadata)

        self.encoding = encoding
        self.path = Path(path)
        if not self.path.is_file():
            raise InvArgException("not a valid file: {}", self.path)


    def iter_simple(self, base: Path):
        it = base.iterdir() if not self._pattern else \
            base.glob(self._pattern) if not self._recursive else \
            base.rglob(self._pattern)

        for elem in it:
            if elem.is_file():
                yield elem


    def iter_recursive(self, base: Path):
        for elem in base.iterdir():
            if elem.is_file():
                yield elem
            elif elem.is_dir():
                yield from self.iter_recursive(elem)


    def iter_doc(self) -> Iterable[SrcDocument]:
        with openfile(self.path, "rt", encoding=self.encoding) as f:
            for line in f:
                try:
                    data = json.loads(line)
                except json.JSONDecodeError as e:
                    raise
                
        it = self.iter_recursive if self._recursive and not self._pattern else self.iter_simple

        for elem in it(self.base):
            yield self._loader(elem)
