
from pathlib import Path

from unittest.mock import Mock
import pytest

from pii_data.helper.exception import InvArgException
from pii_data.types.doc import LocalSrcDocument
import pii_data.types.doc.document as docmod

import pii_preprocess.collection.src.folder as mod


DATADIR = Path(__file__).parents[2] / "data"

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
    obj = mod.FolderDocumentCollection(DATADIR / "text")
    assert str(obj) == "<FolderDocumentCollection: text>"


def test110_constructor():
    """Test object creation, config file"""
    cfg = DATADIR / "config" / "test-loader.json"
    obj = mod.FolderDocumentCollection(DATADIR / "text", config=cfg)
    assert str(obj) == "<FolderDocumentCollection: text>"


def test120_constructor_invalid():
    """Test invalid folder"""
    with pytest.raises(InvArgException) as e:
        mod.FolderDocumentCollection(DATADIR / "not-a-dir")
    assert str(e.value) == f"invalid folder: {DATADIR / 'not-a-dir'}"


def test200_load(fix_uuid):
    """
    Load documents
    """
    obj = mod.FolderDocumentCollection(DATADIR / "text" / "lang")
    for n, doc in enumerate(obj, start=1):
        assert isinstance(doc, docmod.SrcDocument)
        assert doc.id == "33333-22222"

    assert n == 4


def test210_load_glob(fix_uuid):
    """
    Load documents w/ globbing pattern
    """
    obj = mod.FolderDocumentCollection(DATADIR / "text" / "lang",
                                       glob='*-indian-ocean.*')
    for n, doc in enumerate(obj, start=1):
        assert isinstance(doc, docmod.SrcDocument)
        assert doc.id == "33333-22222"

    assert n == 2


def test210_load_glob_rec(fix_uuid):
    """
    Load documents w/ globbing pattern, recursive
    """
    obj = mod.FolderDocumentCollection(DATADIR / "text", recursive=True,
                                       glob='*-indian-ocean.*')
    for n, doc in enumerate(obj, start=1):
        assert isinstance(doc, docmod.SrcDocument)
        assert doc.id == "33333-22222"

    assert n == 2
    
