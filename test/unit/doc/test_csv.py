
from types import MappingProxyType
from pathlib import Path
import tempfile

from unittest.mock import Mock
import pytest

from pii_data.helper.io import load_yaml
import pii_data.types.document as docmod

import pii_preprocess.doc.csv as mod


DATA = [
    ["2021-03-01", "John Smith", "4273 9666 4581 5642", "USD", "12.39", "Our Iceberg Is Melting: Changing and Succeeding Under Any Conditions"],
    ["2022-09-10", "Erik Jonsk", "4273 9666 4581 5642", "EUR", "11.99", "Bedtime Originals Choo Choo Express Plush Elephant - Humphrey"],
    ["2022-09-11", "John Smith", "4273 9666 4581 5642", "USD", "339.99", "Robot Vacuum Mary, Nobuk Robotic Vacuum Cleaner and Mop, 5000Pa Suction, Intelligent AI Mapping, Virtual Walls, Ideal for Pets Hair, Self-Charging, Carpets, Hard Floors, Tile, Wi-Fi, App Control"]
]


CHUNKS = [
    {'id': 'R1.1', 'data': '2021-03-01',
     'context': {'column': {'number': 1, 'name': 'Date'}, "row": "R1"}},
    {'id': 'R1.2', 'data': 'John Smith',
     'context': {'column': {'number': 2, 'name': 'Name'}, "row": "R1"}},
    {'id': 'R1.3', 'data': '4273 9666 4581 5642',
     'context': {'column': {'number': 3, 'name': 'Credit Card'}, "row": "R1"}},
    {'id': 'R1.4', 'data': 'USD',
     'context': {'column': {'number': 4, 'name': 'Currency'}, "row": "R1"}},
    {'id': 'R1.5', 'data': '12.39',
     'context': {'column': {'number': 5, 'name': 'Amount'}, "row": "R1"}},
    {'id': 'R1.6', 'data': 'Our Iceberg Is Melting: Changing and Succeeding Under Any Conditions',
     'context': {'column': {'number': 6, 'name': 'Description'}, "row": "R1"}},
    {'id': 'R2.1', 'data': '2022-09-10',
     'context': {'column': {'number': 1, 'name': 'Date'}, "row": "R2"}},
    {'id': 'R2.2', 'data': 'Erik Jonsk',
     'context': {'column': {'number': 2, 'name': 'Name'}, "row": "R2"}},
    {'id': 'R2.3', 'data': '4273 9666 4581 5642',
     'context': {'column': {'number': 3, 'name': 'Credit Card'}, "row": "R2"}},
    {'id': 'R2.4', 'data': 'EUR',
     'context': {'column': {'number': 4, 'name': 'Currency'}, "row": "R2"}},
    {'id': 'R2.5', 'data': '11.99',
     'context': {'column': {'number': 5, 'name': 'Amount'}, "row": "R2"}},
    {'id': 'R2.6', 'data': 'Bedtime Originals Choo Choo Express Plush Elephant - Humphrey',
     'context': {'column': {'number': 6, 'name': 'Description'}, "row": "R2"}},
    {'id': 'R3.1', 'data': '2022-09-11',
     'context': {'column': {'number': 1, 'name': 'Date'}, "row": "R3"}},
    {'id': 'R3.2', 'data': 'John Smith',
     'context': {'column': {'number': 2, 'name': 'Name'}, "row": "R3"}},
    {'id': 'R3.3', 'data': '4273 9666 4581 5642',
     'context': {'column': {'number': 3, 'name': 'Credit Card'}, "row": "R3"}},
    {'id': 'R3.4', 'data': 'USD',
     'context': {'column': {'number': 4, 'name': 'Currency'}, "row": "R3"}},
    {'id': 'R3.5', 'data': '339.99',
     'context': {'column': {'number': 5, 'name': 'Amount'}, "row": "R3"}},
    {'id': 'R3.6', 'data': 'Robot Vacuum Mary, Nobuk Robotic Vacuum Cleaner and Mop, 5000Pa Suction, Intelligent AI Mapping, Virtual Walls, Ideal for Pets Hair, Self-Charging, Carpets, Hard Floors, Tile, Wi-Fi, App Control',
     'context': {'column': {'number': 6, 'name': 'Description'}, "row": "R3"}}
]



def fname(name: str) -> str:
    return Path(__file__).parents[2] / "data" / "csv" / name

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
    """Test base object creation"""
    obj = mod.CsvDocument()
    assert str(obj) == "<CsvDocument>"


def test110_open():
    """Test open file"""
    obj = mod.CsvDocument()
    filename = fname("table-example.csv")
    with open(filename, encoding="utf-8") as f:
        obj.open(f)
        assert str(obj) == "<CsvDocument>"


def test120_read_base():
    """Test data read"""
    obj = mod.CsvDocument()
    filename = fname("table-example.csv")
    with open(filename, encoding="utf-8") as f:
        obj.open(f)
        got = list(obj.iter_base())

    exp = [{"id": f"R{n}", "data": e} for n, e in enumerate(DATA, start=1)]
    assert exp == got


def test125_read_base_block():
    """Test data read, group rows"""
    obj = mod.CsvDocument()
    filename = fname("table-example.csv")
    with open(filename, encoding="utf-8") as f:
        obj.open(f)
        got = list(obj.iter_base_block(block_size=2))

    exp = [
        {"id": "B1", "data": DATA[0:2]},
        {"id": "B2", "data": DATA[2:]}
    ]
    assert exp == got


def test130_read_chunks():
    """Test data read, in chunks"""
    obj = mod.CsvDocument()
    filename = fname("table-example.csv")
    with open(filename, encoding="utf-8") as f:
        obj.open(f)
        got = list(obj)

    exp = [docmod.DocumentChunk(**c) for c in CHUNKS]
    assert len(exp) == len(got)
    for e, g in zip(exp, got):
        assert e == g


def test200_local():
    """Test local object creation, data"""
    filename = fname("table-example.csv")
    obj = mod.LocalCsvDocument(filename)
    assert str(obj) == f"<CsvDocument file={filename}>"


def test210_read_base():
    """Test document base iteration"""
    filename = fname("table-example.csv")
    obj = mod.LocalCsvDocument(filename)
    obj.open(filename)
    got = list(obj.iter_base())
    obj.close()

    exp = [{"id": f"R{n}", "data": e} for n, e in enumerate(DATA, start=1)]
    assert exp == got


def test220_ctx_manager():
    """Test reading local document, using context manager"""
    with mod.LocalCsvDocument(fname("table-example.csv")) as f:
        got = list(f.iter_base())

    exp = [{"id": f"R{n}", "data": e} for n, e in enumerate(DATA, start=1)]
    assert exp == got


def test300_read_chunks():
    """Test document chunks"""
    filename = fname("table-example.csv")
    obj = mod.LocalCsvDocument(filename)
    obj.open(filename)
    got = list(obj)
    obj.close()
    exp = [docmod.DocumentChunk(**c) for c in CHUNKS]
    assert exp == got


def test310_chunks_ctx_manager():
    """Test reading local document, using context manager"""
    with mod.LocalCsvDocument(fname("table-example.csv")) as f:
        got = list(f)

    exp = [docmod.DocumentChunk(**c) for c in CHUNKS]
    assert exp == got


def test320_read_chunks_context(fix_uuid):
    """Test document chunks, context"""
    name = fname("table-example.csv")
    obj = mod.LocalCsvDocument(name, id_path_prefix=False,
                               iter_options={'context': True})
    got = list(obj)
    obj.close()

    ctx_doc = MappingProxyType({"type": "table", "origin": "csv",
                                "id": "00000-11111"})

    # Check the first chunk
    assert got[0] == docmod.DocumentChunk(
        id=CHUNKS[0]['id'],
        data=CHUNKS[0]['data'],
        context={"document": ctx_doc,
                 "column": {"name": "Date", "number": 1},
                 "row": "R1",
                 "after": CHUNKS[1]['data']}
    )

    # Check all chunks
    exp = [
        docmod.DocumentChunk(
            id=e['id'],
            data=e['data'],
            context={"document": ctx_doc,
                     "column": e["context"]["column"],
                     "row": e["context"]["row"],
                     "before": CHUNKS[n-1]['data'] if n else None,
                     "after": CHUNKS[n+1]['data'] if n<len(CHUNKS)-1 else None}
        )
        for n, e in enumerate(CHUNKS)
    ]
    del exp[0].context['before']
    del exp[-1].context['after']

    assert exp == got


def test320_read_chunks_context_meta():
    """Test object creation, multiple chunks, context, metadata"""
    obj = mod.LocalCsvDocument(fname("table-example.csv"),
                               iter_options={'context': True})
    obj.add_metadata(document={"lang": "en"}, dataset={"name": "BigDataset"})
    obj.set_id("abc")
    got = list(obj)
    obj.close()

    ctx_doc = MappingProxyType({"id": "abc", "lang": "en", "type": "table",
                                "origin": "csv"})
    ctx_ds = MappingProxyType({"name": "BigDataset"})
    exp = [
        docmod.DocumentChunk(
            id=e['id'],
            data=e['data'],
            context={"document": ctx_doc,
                     "dataset": ctx_ds,
                     "column": e["context"]["column"],
                     "row": e["context"]["row"],
                     "before": CHUNKS[n-1]['data'] if n else None,
                     "after": CHUNKS[n+1]['data'] if n<len(CHUNKS)-1 else None}
        )
        for n, e in enumerate(CHUNKS)
    ]
    del exp[0].context['before']
    del exp[-1].context['after']

    assert exp == got


def test400_dump(fix_uuid):
    """Test object dump"""

    filename = fname("table-example.csv")
    obj = mod.LocalCsvDocument(filename, id_path_prefix=False)

    try:
        f = tempfile.NamedTemporaryFile(mode="wt", suffix=".yml", delete=False)
        obj.dump(f.name)
        got = load_yaml(f.name)
    finally:
        #print(f.name)
        Path(f.name).unlink()

    exp = load_yaml(fname("table-example.yml"))
    assert exp == got
