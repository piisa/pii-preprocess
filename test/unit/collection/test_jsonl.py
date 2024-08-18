
from pathlib import Path

from unittest.mock import Mock
import pytest

from pii_data.helper.exception import InvArgException
import pii_data.types.doc.document as docmod

import pii_preprocess.collection.src.jsonl as mod


DATADIR = Path(__file__).parents[2] / "data"
TESTFILE = DATADIR / "collection" / "test-collection.jsonl"


def readfile(name: str) -> str:
    with open(name, "rt", encoding="utf-8") as f:
        return f.read().strip()

@pytest.fixture
def fix_uuid(monkeypatch):
    """
    Monkey-patch the document module to ensure a fixed uuid
    """
    mock_uuid = Mock()
    mock_uuid.uuid4 = Mock(return_value="33333-22222")
    monkeypatch.setattr(docmod, "uuid", mock_uuid)


# ----------------------------------------------------------------


def test100_constructor():
    """Test object creation"""
    obj = mod.JsonlDocumentCollection(TESTFILE)
    assert str(obj) == "<JsonlDocumentCollection: test-collection.jsonl>"


def test110_constructor():
    """Test object creation, config file"""
    cfg = DATADIR / "config" / "test-loader.json"
    obj = mod.JsonlDocumentCollection(TESTFILE, config=cfg)
    assert str(obj) == "<JsonlDocumentCollection: test-collection.jsonl>"


def test120_constructor_invalid():
    """Test invalid file"""
    with pytest.raises(InvArgException) as e:
        mod.JsonlDocumentCollection(DATADIR / "not-a-file")
    assert str(e.value) == f"not a valid file: {DATADIR / 'not-a-file'}"


def test200_load(fix_uuid):
    """
    Load documents
    """
    IDLIST = ("00000-11111", "00000-22222")
    obj = mod.JsonlDocumentCollection(TESTFILE)
    for n, (doc, docid) in enumerate(zip(obj, IDLIST), start=1):
        assert isinstance(doc, docmod.SrcDocument)
        assert doc.id == docid

    assert n == 2
