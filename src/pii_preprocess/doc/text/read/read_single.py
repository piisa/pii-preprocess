"""
Read a text document as a single chunk
"""

from pii_data.types.localdoc import SequenceLocalSrcDocument

from .base import BaseReader


class SingleReader(BaseReader):
    """
    Read a text file as a single chunk
    """

    def read(self, inputfile: str,
             encoding: str = 'utf-8') -> SequenceLocalSrcDocument:
        """
        Read a local text file
        """
        doc = super().read(inputfile, encoding)
        return SequenceLocalSrcDocument(chunks=[doc], metadata=self.meta,
                                        **self.kwargs)
