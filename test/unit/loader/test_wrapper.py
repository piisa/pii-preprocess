
from pathlib import Path

from unittest.mock import Mock
import pytest

from pii_data.helper.exception import ProcException
from pii_data.defs import FMT_CONFIG_PREFIX
import pii_data.types.doc.document as docmod

from pii_preprocess.defs import FMT_CONFIG_LOADER, PII_PREPROCESS_PLUGIN_ID
import pii_preprocess.loader.wrapper as mod
import pii_preprocess.loader.utils as modutils

from taux.monkey_patch import patch_uuid, patch_entry_points

NUM_LOADERS = 6

DATADIR = Path(__file__).parents[2] / "data"

def readfile(name: str) -> str:
    with open(name, "rt", encoding="utf-8") as f:
        return f.read().strip()

@pytest.fixture
def fix_uuid(monkeypatch):
    patch_uuid(monkeypatch)

@pytest.fixture
def fix_entry_points(monkeypatch):
    patch_entry_points(monkeypatch)


# ----------------------------------------------------------------


def test100_constructor():
    """Test object creation"""
    obj = mod.LoaderWrapper()
    assert str(obj) == f"<LoaderWrapper #{NUM_LOADERS}>"


def test110_constructor():
    """Test object creation, config file"""
    obj = mod.LoaderWrapper(DATADIR / "config" / "test-loader-wrapper.json")
    assert str(obj) == f"<LoaderWrapper #{NUM_LOADERS + 2}>"


def test120_constructor(fix_uuid, fix_entry_points):
    """Test object creation, config file, plugins"""
    obj = mod.LoaderWrapper(DATADIR / "config" / "test-loader-wrapper.json")
    assert str(obj) == f"<LoaderWrapper #{NUM_LOADERS + 4}>"


def test200_load_invalid():
    """Test invalid document load"""
    obj = mod.LoaderWrapper()
    name = DATADIR / "example.blargh"
    with pytest.raises(ProcException) as e:
        list(obj.load(name))
    assert str(e.value) == f"cannot find a mime type for file: {name}"


def test210_load_invalid(fix_uuid):
    """Test error in document load"""
    obj = mod.LoaderWrapper()
    fakeconf = {"format": FMT_CONFIG_PREFIX + FMT_CONFIG_LOADER,
                "loaders": {"text/plain": {"class": "non.existing.class"}}}
    obj.add_config(fakeconf)
    name = DATADIR / "text" / "doc-example.txt"
    with pytest.raises(ProcException) as e:
        list(obj.load(name))
    assert str(e.value) == "cannot import object 'non.existing.class': No module named 'non'"


def test300_load_yml():
    """Test YAML document load"""
    obj = mod.LoaderWrapper()
    wrp = obj.load(DATADIR / "msword" / "example-headings.yml")
    doc = list(wrp)
    assert len(doc) == 1
    assert str(doc[0]) == "<SrcDocument 00000-11111>"


def test310_load_text():
    """Test text document load"""
    obj = mod.LoaderWrapper()
    wrp = obj.load(DATADIR / "msword" / "example-headings.yml")
    doc = list(wrp)
    assert len(doc) == 1
    assert str(doc[0]) == "<SrcDocument 00000-11111>"


def test320_load_msword(fix_uuid):
    """Test MSWord document load"""
    obj = mod.LoaderWrapper()
    wrp = obj.load(DATADIR / "msword" / "example-headings.docx")
    doc = list(wrp)
    assert len(doc) == 1
    assert str(doc[0]) == "<SrcDocument 11111-22222>"


def test330_load_csv(fix_uuid):
    """Test CSV document load"""
    obj = mod.LoaderWrapper()
    name = DATADIR / "csv" / "table-example.csv"
    wrp = obj.load(name)
    doc = list(wrp)
    assert len(doc) == 1
    assert str(doc[0]) == f"<CsvDocument file={name}>"


def test350_load_collection(fix_uuid):
    """Test collection load"""
    obj = mod.LoaderWrapper()
    name = DATADIR / "text" / "lang"
    wrp = obj.load(name)
    doc = list(wrp)
    assert len(doc) == 4
