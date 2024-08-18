
import tempfile
from pathlib import Path

import pytest


from pii_data.helper.exception import InvArgException
from pii_data.types.doc import SrcDocument

import pii_preprocess.collection.save as mod


DATADIR = Path(__file__).parents[2] / "data"


class EmptyDocument(SrcDocument):

    def __init__(self, num):
        super().__init__()
        self.set_id(num)

    def iter_base(self):
        return []


# ----------------------------------------------------------------


def test100_constructor_dir():
    """Test object creation, directory"""
    with tempfile.TemporaryDirectory() as dirname:
        mod.CollectionSaver(dirname, "txt")


def test110_constructor_file():
    """Test object creation, file"""
    with tempfile.NamedTemporaryFile() as f:
        f.close()
        mod.CollectionSaver(f.name, "ndjson")


def test120_constructor_err():
    """Test object creation, invalid directory destination"""
    with tempfile.NamedTemporaryFile() as f:
        f.close()
        with pytest.raises(InvArgException):
            mod.CollectionSaver(f.name, "txt")


def test200_write():
    """Test object creation"""
    with tempfile.TemporaryDirectory() as dirname:
        obj = mod.CollectionSaver(dirname, "txt")
        for n in range(2):
            doc = EmptyDocument(str(n))
            obj.save(doc)

        dest = Path(dirname)
        exp = [dest / "001-0.txt", dest / "002-1.txt"]
        got = sorted(dest.iterdir())
        assert exp == got
