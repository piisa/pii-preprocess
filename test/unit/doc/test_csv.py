
from types import MappingProxyType
from pathlib import Path
import tempfile

from unittest.mock import Mock
import pytest

from pii_data.helper.io import load_yaml
from pii_data.types.doc.chunker import DocumentChunk
import pii_data.types.doc.document as docmod

import pii_preprocess.doc.csv as mod


NAMES = ["Date", "Name", "Credit Card", "Currency", "Amount", "Description"]
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


DATADIR = Path(__file__).parents[2] / "data" / "csv"

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


@pytest.fixture
def fix_tstamp(monkeypatch):
    """
    Monkey-patch the file modification time call
    """
    mock_st = Mock()
    mock_st.st_mtime = 20
    mock_os = Mock()
    mock_os.stat = Mock(return_value=mock_st)
    monkeypatch.setattr(mod, "os", mock_os)


# ----------------------------------------------------------------

class myTestClass1(mod.CsvDocument):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_metadata(column={'name': NAMES})

    def get_base_iter(self):
        return iter(DATA)


class myTestClass2(mod.TextIOCsvDocument):

    def open(self):
        return open(DATADIR / "table-example.csv", encoding="utf-8")


# ----------------------------------------------------------------

def test100_constructor(fix_uuid):
    """Test base object creation"""
    obj = mod.CsvDocument()
    assert str(obj) == "<CsvDocument>"


def test110_open():
    """Test open file"""
    obj = myTestClass1()
    assert str(obj) == "<CsvDocument>"


def test120_read_base():
    """Test data read"""
    obj = myTestClass1()
    got = list(obj.iter_base())
    exp = [{"id": f"R{n}", "data": e} for n, e in enumerate(DATA, start=1)]
    assert exp == got


def test125_read_base_block():
    """Test data read, group rows"""
    obj = myTestClass1()
    got = list(obj.iter_base_block(block_size=2))
    exp = [
        {"id": "B1", "data": DATA[0:2]},
        {"id": "B2", "data": DATA[2:]}
    ]
    assert exp == got


def test130_read_chunks():
    """Test data read, in chunks"""
    obj = myTestClass1()
    got = list(obj)
    exp = [DocumentChunk(**c) for c in CHUNKS]
    assert len(exp) == len(got)
    for e, g in zip(exp, got):
        assert e == g


def test220_read_base():
    """Test data read"""
    obj = myTestClass2()
    got = list(obj.iter_base())
    exp = [{"id": f"R{n}", "data": e} for n, e in enumerate(DATA, start=1)]
    assert exp == got


def test225_read_base_block():
    """Test data read, group rows"""
    obj = myTestClass2()
    got = list(obj.iter_base_block(block_size=2))
    exp = [
        {"id": "B1", "data": DATA[0:2]},
        {"id": "B2", "data": DATA[2:]}
    ]
    assert exp == got


def test230_read_chunks():
    """Test data read, in chunks"""
    obj = myTestClass2()
    got = list(obj)
    exp = [DocumentChunk(**c) for c in CHUNKS]
    assert len(exp) == len(got)
    for e, g in zip(exp, got):
        assert e == g


def test300_local():
    """Test local object creation"""
    filename = DATADIR / "table-example.csv"
    obj = mod.LocalCsvDocument(filename)
    assert str(obj) == f"<CsvDocument file={filename}>"


def test301_local_meta(fix_tstamp):
    """Test local object, metadata"""
    filename = DATADIR / "table-example.csv"
    obj = mod.LocalCsvDocument(filename)
    exp = {
        'document': {
            'id': str(filename),
            'type': 'table',
            'origin': 'csv',
            'date': '1970-01-01T00:00:20'
        },
        'column': {
            'name': ['Date', 'Name', 'Credit Card', 'Currency',
                     'Amount', 'Description']
        }
    }
    assert exp == dict(**obj.metadata)


def test302_local_meta_path(fix_tstamp, fix_uuid):
    """Test local object, metadata, no path id"""
    filename = DATADIR / "table-example.csv"
    obj = mod.LocalCsvDocument(filename, id_path_prefix=False)
    exp = {
        'document': {
            'id': '00000-11111',
            'type': 'table',
            'origin': 'csv',
            'date': '1970-01-01T00:00:20'
        },
        'column': {
            'name': ['Date', 'Name', 'Credit Card', 'Currency',
                     'Amount', 'Description']
        }
    }
    assert exp == dict(**obj.metadata)


def test303_local_meta_id(fix_tstamp, fix_uuid):
    """Test local object, metadata, doc id"""
    filename = DATADIR / "table-example.csv"
    obj = mod.LocalCsvDocument(filename, id_path_prefix=False,
                               metadata={"document": {"id": "abc"}})
    exp = {
        'document': {
            'id': 'abc',
            'type': 'table',
            'origin': 'csv',
            'date': '1970-01-01T00:00:20'
        },
        'column': {
            'name': ['Date', 'Name', 'Credit Card', 'Currency',
                     'Amount', 'Description']
        }
    }
    assert exp == dict(**obj.metadata)



def test310_read_base():
    """Test document base iteration"""
    filename = fname("table-example.csv")
    obj = mod.LocalCsvDocument(filename)
    obj.open()
    got = list(obj.iter_base())
    obj.close()

    exp = [{"id": f"R{n}", "data": e} for n, e in enumerate(DATA, start=1)]
    assert exp == got


def test320_ctx_manager():
    """Test reading local document, using context manager"""
    with mod.LocalCsvDocument(fname("table-example.csv")) as f:
        got = list(f.iter_base())

    exp = [{"id": f"R{n}", "data": e} for n, e in enumerate(DATA, start=1)]
    assert exp == got


def test400_read_chunks():
    """Test document chunks"""
    filename = fname("table-example.csv")
    obj = mod.LocalCsvDocument(filename)
    obj.open()
    got = list(obj)
    obj.close()
    exp = [DocumentChunk(**c) for c in CHUNKS]
    assert exp == got


def test401_read_chunks_repeat():
    """Test document chunks, repeatedly"""
    filename = fname("table-example.csv")
    obj = mod.LocalCsvDocument(filename)
    obj.open()

    got = list(obj)
    exp = [DocumentChunk(**c) for c in CHUNKS]
    assert exp == got

    got = list(obj)
    exp = [DocumentChunk(**c) for c in CHUNKS]
    assert exp == got


def test410_chunks_ctx_manager():
    """Test reading local document, using context manager"""
    with mod.LocalCsvDocument(fname("table-example.csv")) as f:
        got = list(f)

    exp = [DocumentChunk(**c) for c in CHUNKS]
    assert exp == got


def test420_read_chunks_context(fix_uuid, fix_tstamp):
    """Test document chunks, context"""
    name = fname("table-example.csv")
    obj = mod.LocalCsvDocument(name, id_path_prefix=False,
                               iter_options={'context': True})
    got = list(obj)
    obj.close()

    ctx_doc = MappingProxyType({"type": "table", "origin": "csv",
                                "id": "00000-11111",
                                "date": "1970-01-01T00:00:20"})

    # Check the first chunk
    assert got[0] == DocumentChunk(
        id=CHUNKS[0]['id'],
        data=CHUNKS[0]['data'],
        context={"document": ctx_doc,
                 "column": {"name": "Date", "number": 1},
                 "row": "R1",
                 "after": CHUNKS[1]['data']}
    )

    # Check all chunks
    exp = [
        DocumentChunk(
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

    assert len(exp) == len(got)
    assert exp == got


def test420_read_chunks_context_meta(fix_tstamp):
    """Test object creation, multiple chunks, context, metadata"""
    obj = mod.LocalCsvDocument(fname("table-example.csv"),
                               iter_options={'context': True})
    obj.add_metadata(document={"lang": "en"}, dataset={"name": "BigDataset"})
    obj.set_id("abc")
    got = list(obj)
    obj.close()

    ctx_doc = MappingProxyType({"id": "abc", "lang": "en", "type": "table",
                                "origin": "csv", "date": "1970-01-01T00:00:20"})
    ctx_ds = MappingProxyType({"name": "BigDataset"})
    exp = [
        DocumentChunk(
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

    assert len(exp) == len(got)
    assert exp == got


def test500_dump(fix_uuid, fix_tstamp):
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
