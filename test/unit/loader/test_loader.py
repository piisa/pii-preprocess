
from pathlib import Path

from unittest.mock import Mock
import pytest

from pii_data.helper.exception import ProcException
from pii_data.defs import FMT_CONFIG_PREFIX
import pii_data.types.doc.document as docmod

from pii_preprocess.defs import FMT_CONFIG_LOADER
import pii_preprocess.loader.loader as mod


NUM_LOADERS = 6

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
    assert str(obj) == f"<DocumentLoader #{NUM_LOADERS}>"


def test110_constructor(fix_uuid):
    """Test object creation, config file"""
    obj = mod.DocumentLoader(DATADIR / "config" / "test-loader.json")
    assert str(obj) == f"<DocumentLoader #{NUM_LOADERS+1}>"


def test120_load_invalid(fix_uuid):
    """Test invalid document load"""
    obj = mod.DocumentLoader()
    name = DATADIR / "example.blargh"
    with pytest.raises(ProcException) as e:
        obj.load(name)
    assert str(e.value) == f"cannot find a mime type for file: {name}"

def test121_load_invalid(fix_uuid):
    """Test invalid config for document load"""
    fakeconf = {"format": FMT_CONFIG_PREFIX + FMT_CONFIG_LOADER,
                "loaders": {"text/plain": {"class": "non.existing.class"}}}
    obj = mod.DocumentLoader({FMT_CONFIG_LOADER: fakeconf})
    name = DATADIR / "example.txt"
    with pytest.raises(ProcException) as e:
        obj.load(name)
    assert str(e.value) == "cannot import object 'non.existing.class': No module named 'non'"


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
