
from pathlib import Path

from pii_data.types.doc import SrcDocument

import pii_preprocess.collection.base as mod


DATADIR = Path(__file__).parents[2] / "data"


class UnitTestCollection(mod.DocumentCollection):

    def iter_doc(self):
        for n in range(3):
            yield SrcDocument(metadata={"document": {"id": str(n)}})


# ----------------------------------------------------------------


def test100_constructor():
    """Test object creation"""
    obj = mod.DocumentCollection()
    assert str(obj) == "<DocumentCollection>"


def test110_constructor():
    """Test object creation, config file"""
    obj = mod.DocumentCollection(DATADIR / "config" / "test-loader.json")
    assert str(obj) == "<DocumentCollection>"


def test120_load():
    """Test collection iteration"""
    obj = UnitTestCollection()

    for n, doc in enumerate(obj):
        assert isinstance(doc, SrcDocument)
        assert doc.id == str(n)

    assert n == 2
