
from pathlib import Path
import tempfile

from unittest.mock import Mock
import pytest


from pii_data.helper.io import load_yaml
import pii_preprocess.doc.csv as mod
import pii_data.types.document as docmod


DATA = [
    ["2021-03-01", "John Smith", "4273 9666 4581 5642", "USD", "12.39", "Our Iceberg Is Melting: Changing and Succeeding Under Any Conditions"],
    ["2022-09-10", "Erik Jonsk", "4273 9666 4581 5642", "EUR", "11.99", "Bedtime Originals Choo Choo Express Plush Elephant - Humphrey"],
    ["2022-09-11", "John Smith", "4273 9666 4581 5642", "USD", "339.99", "Robot Vacuum Mary, Nobuk Robotic Vacuum Cleaner and Mop, 5000Pa Suction, Intelligent AI Mapping, Virtual Walls, Ideal for Pets Hair, Self-Charging, Carpets, Hard Floors, Tile, Wi-Fi, App Control"]
]



def fname(name: str) -> str:
    return Path(__file__).parents[2] / "data" / name

def readfile(name: str) -> str:
    with open(name, "rt", encoding="utf-8") as f:
        return f.read().strip()

@pytest.fixture
def fix_uuid(monkeypatch):
    """
    Monkey-patch the document module to ensure a fixed uuid
    """
    mock_uuid = Mock()
    mock_uuid.uuid4 = Mock(return_value="00000-11111")
    monkeypatch.setattr(docmod, "uuid", mock_uuid)


# ----------------------------------------------------------------


def test100_constructor(fix_uuid):
    """Test object creation"""
    obj = mod.CsvDocument()
    assert str(obj) == "<CsvDocument>"


def test110_open():
    """Test object creation, data"""
    obj = mod.CsvDocument()
    filename = fname("doc-example.csv")
    with open(filename, encoding="utf-8") as f:
        obj.open(f)
        assert str(obj) == "<CsvDocument>"


def test120_read():
    """Test object creation, data"""
    obj = mod.CsvDocument()
    filename = fname("doc-example.csv")
    with open(filename, encoding="utf-8") as f:
        obj.open(f)
        got = list(obj)

    exp = [
        docmod.DocumentChunk(id="1", data=DATA)
    ]
    assert exp == got


def test200_local():
    """Test object creation, data"""
    filename = fname("doc-example.csv")
    obj = mod.LocalCsvDocument(filename)
    assert str(obj) == f"<CsvDocument {filename}>"



def test210_read_chunks():
    """Test document chunks, multiple chunks"""
    filename = fname("doc-example.csv")
    obj = mod.LocalCsvDocument(filename, chunk_size=2)
    obj.open(filename)
    got = list(obj)
    obj.close()

    exp = [
        docmod.DocumentChunk(id="1", data=DATA[0:2]),
        docmod.DocumentChunk(id="2", data=DATA[2:3])
    ]
    assert exp == got


def test220_ctx_manager():
    """Test reading local document, using context manager"""
    with mod.LocalCsvDocument(fname("doc-example.csv"), chunk_size=2) as f:
        got = list(f)

    exp = [
        docmod.DocumentChunk(id="1", data=DATA[0:2]),
        docmod.DocumentChunk(id="2", data=DATA[2:3])
    ]
    assert exp == got


def test230_dump(fix_uuid):
    """Test object dump"""

    filename = fname("doc-example.csv")
    obj = mod.LocalCsvDocument(filename, id_path_prefix=False)

    try:
        f = tempfile.NamedTemporaryFile(mode="wt", suffix=".yml", delete=False)
        obj.dump(f.name)
        got = load_yaml(f.name)
    finally:
        Path(f.name).unlink()

    exp = load_yaml(fname("doc-example.yaml"))
    assert exp == got


def test300_read_chunks_context(fix_uuid):
    """Test document chunks, context"""
    name = fname("doc-example.csv")
    obj = mod.LocalCsvDocument(name, id_path_prefix=False,
                               add_chunk_context=True)
    got = list(obj)
    obj.close()

    ctx_doc = {"id": "00000-11111", "type": "tabular"}
    ctx_col = {"name": ["Date", "Name", "Credit Card", "Currency", "Amount", "Description"]}
    exp = [
        docmod.DocumentChunk(id="1", data=DATA,
                             context={"document": ctx_doc, "column": ctx_col})
    ]
    assert exp == got


def test310_read_chunks_context():
    """Test object creation, multiple chunks, context"""

    name = fname("doc-example.csv")
    obj = mod.LocalCsvDocument(name, id_path_prefix=name.parent, chunk_size=2,
                               add_chunk_context=True)
    ctx_doc = {"id": "doc-example.csv", "type": "tabular"}
    ctx_col = {"name": ["Date", "Name", "Credit Card", "Currency", "Amount", "Description"]}
    exp = [
        docmod.DocumentChunk(id="1", data=DATA[0:2],
                             context={"document": ctx_doc,
                                      "column": ctx_col,
                                      "after": DATA[2:3]}),
        docmod.DocumentChunk(id="2", data=DATA[2:3],
                             context={"document": ctx_doc,
                                      "column": ctx_col,
                                      "before": DATA[0:2]}),
    ]
    got = list(obj)
    assert exp == got


def test320_read_chunks_context_meta():
    """Test object creation, multiple chunks, context, metadata"""
    obj = mod.LocalCsvDocument(fname("doc-example.csv"),
                               chunk_size=2, add_chunk_context=True)
    obj.add_metadata(document={"lang": "en"}, dataset={"name": "BigDataset"})
    obj.set_id("abc")
    got = list(obj)
    obj.close()

    ctx_doc = {"id": "abc", "lang": "en", "type": "tabular"}
    ctx_ds = {"name": "BigDataset"}
    ctx_col = {"name": ["Date", "Name", "Credit Card", "Currency", "Amount", "Description"]}
    exp = [
        docmod.DocumentChunk(id="1", data=DATA[0:2],
                             context={"document": ctx_doc,
                                      "dataset": ctx_ds,
                                      "column": ctx_col,
                                      "after": DATA[2:3]}),
        docmod.DocumentChunk(id="2", data=DATA[2:3],
                             context={"document": ctx_doc,
                                      "dataset": ctx_ds,
                                      "column": ctx_col,
                                      "before": DATA[0:2]}),
    ]
    assert exp == got
