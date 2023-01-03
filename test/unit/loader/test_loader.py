
from pathlib import Path

from unittest.mock import Mock
import pytest

from pii_data.helper.exception import ProcException
import pii_data.types.doc.document as docmod

import pii_preprocess.loader.loader as mod


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
    mock_uuid.uuid4 = Mock(return_value="11111-22222")
    monkeypatch.setattr(docmod, "uuid", mock_uuid)


# ----------------------------------------------------------------


def test100_constructor(fix_uuid):
    """Test object creation"""
    obj = mod.DocumentLoader()
    assert str(obj) == "<DocumentLoader 4>"


def test110_constructor(fix_uuid):
    """Test object creation, config file"""
    obj = mod.DocumentLoader(DATADIR / "test-loader.json")
    assert str(obj) == "<DocumentLoader 5>"


def test120_load_invalid(fix_uuid):
    """Test invalid document load"""
    obj = mod.DocumentLoader()
    name = DATADIR / "example.blargh"
    with pytest.raises(ProcException) as e:
        obj.load(name)
    assert str(e.value) == f"cannot find a type for file: {name}"

def test121_load_invalid(fix_uuid):
    """Test error in document load"""
    obj = mod.DocumentLoader()
    fakeconf = {"loaders": { "text/plain": {"class": "a.non.existing.class"}}}
    obj.add_config(fakeconf)
    name = DATADIR / "example.txt"
    with pytest.raises(ProcException) as e:
        obj.load(name)
    assert str(e.value) == "cannot import object 'a.non.existing.class': No module named 'a'"


def test200_load_yml():
    """Test YAML document load"""
    obj = mod.DocumentLoader()
    doc = obj.load(DATADIR / "msword" / "example-headings.yml")
    assert str(doc) == "<SrcDocument 00000-11111>"


def test210_load_text():
    """Test text document load"""
    obj = mod.DocumentLoader()
    doc = obj.load(DATADIR / "msword" / "example-headings.yml")
    assert str(doc) == "<SrcDocument 00000-11111>"


def test220_load_msword(fix_uuid):
    """Test MSWord document load"""
    obj = mod.DocumentLoader()
    doc = obj.load(DATADIR / "msword" / "example-headings.docx")
    assert str(doc) == "<SrcDocument 11111-22222>"


def test230_load_csv(fix_uuid):
    """Test CSV document load"""
    obj = mod.DocumentLoader()
    name = DATADIR / "csv" / "table-example.csv"
    doc = obj.load(name)
    assert str(doc) == f"<CsvDocument file={name}>"
