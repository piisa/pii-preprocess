
from pathlib import Path
import tempfile
import json
import datetime

from unittest.mock import Mock
import pytest

from pii_data.helper.json_encoder import CustomJSONEncoder
from pii_data.helper.io import load_yaml
import pii_data.types.doc.document as docmod

import pii_preprocess.doc.msoffice.msexcel as mod


DATADIR = Path(__file__).parents[2] / "data" / "msexcel"

def readfile(name: str) -> str:
    with open(name, "rt", encoding="utf-8") as f:
        return f.read().strip()

def read_json(name: str) -> str:
    with open(name, "rt", encoding="utf-8") as f:
        return json.load(f)

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
    obj = mod.ExcelDocument(DATADIR / "table-example.xlsx")
    assert isinstance(obj, docmod.TableSrcDocument)
    assert str(obj) == "<SrcDocument 00000-11111>"


def test110_header(fix_uuid):
    """Test object metadata"""
    obj = mod.ExcelDocument(DATADIR / "table-example.xlsx")
    meta = {
        "document": {
            "origin": "msexcel",
            "type": "table",
            "title": "Example workbook",
            "sheetname": "table-example",
            "subject": "PIISA",
            "id": "00000-11111",
            "date": "2024-03-25T18:49:24"
        },
        "column": {
            'name': ['Date', 'Name', 'Credit Card', 'Currency', 'Amount', 'Description']
        }
    }
    #print(obj.metadata, meta, sep="\n")
    assert obj.metadata == meta


def test120_iter_struct():
    """Test struct iteration, w/ header row"""
    obj = mod.ExcelDocument(DATADIR / "table-example.xlsx")

    try:
        f = tempfile.NamedTemporaryFile(mode="wt", suffix=".json", delete=False)
        with open(f.name, "wt", encoding="utf-8") as o:
            json.dump(obj.iter_struct(), o, cls=CustomJSONEncoder,
                      ensure_ascii=False, indent=2)
        got = read_json(f.name)
    finally:
        #print(f.name)
        Path(f.name).unlink()

    exp = read_json(DATADIR / "table-example-rows.json")
    assert exp == got

    # def expand(d):
    #     return {k: list(v) if isinstance(v, GeneratorType) else v
    #             for k, v in d.items()}
    # got = list(expand(v) for v in obj.iter_struct())


def test121_iter_struct_nohdr():
    """Test struct iteration, wo/ header row"""
    obj = mod.ExcelDocument(DATADIR / "table-example.xlsx", header=False)

    try:
        f = tempfile.NamedTemporaryFile(mode="wt", suffix=".json", delete=False)
        with open(f.name, "wt", encoding="utf-8") as o:
            json.dump(obj.iter_struct(), o, cls=CustomJSONEncoder,
                      ensure_ascii=False, indent=2)
        got = read_json(f.name)
    finally:
        #print(f.name)
        Path(f.name).unlink()

    exp = read_json(DATADIR / "table-example-rows-noh.json")
    assert exp == got


def test130_iter_full():
    """Test full iteration"""
    obj = mod.ExcelDocument(DATADIR / "table-example.xlsx")

    try:
        f = tempfile.NamedTemporaryFile(mode="wt", suffix=".json", delete=False)
        with open(f.name, "wt", encoding="utf-8") as o:
            json.dump(obj.iter_full(), o, cls=CustomJSONEncoder,
                      ensure_ascii=False, indent=2)
        got = read_json(f.name)
    finally:
        #print(f.name)
        Path(f.name).unlink()

    exp = read_json(DATADIR / "table-example-cells.json")
    assert exp == got


def test131_iter_full_nohdr():
    """Test full iteration, wo/ header row"""
    obj = mod.ExcelDocument(DATADIR / "table-example.xlsx", header=False)

    try:
        f = tempfile.NamedTemporaryFile(mode="wt", suffix=".json", delete=False)
        with open(f.name, "wt", encoding="utf-8") as o:
            json.dump(obj.iter_full(), o, cls=CustomJSONEncoder,
                      ensure_ascii=False, indent=2)
        got = read_json(f.name)
    finally:
        #print(f.name)
        Path(f.name).unlink()

    exp = read_json(DATADIR / "table-example-cells-noh.json")
    assert exp == got



def test140_iter_noctx(fix_uuid):
    """Test chunk iteration, no context"""
    obj = mod.ExcelDocument(DATADIR / "table-example.xlsx",
                            iter_options={"context": False})
    got = list(obj)

    exp = [
        {'id': 'A2', 'data': datetime.datetime(2021, 3, 1, 0, 0)},
        {'id': 'B2', 'data': 'John Smith'},
        {'id': 'C2', 'data': '4273 9666 4581 5642'},
        {'id': 'D2', 'data': 'USD'},
        {'id': 'E2', 'data': 12.39},
        {'id': 'F2', 'data': 'Our Iceberg Is Melting: Changing and Succeeding Under Any Conditions'},

        {'id': 'A3', 'data': datetime.datetime(2022, 9, 10, 0, 0)},
        {'id': 'B3', 'data': 'Erik Jonsk'},
        {'id': 'C3', 'data': '4273 9666 4581 5642'},
        {'id': 'D3', 'data': 'EUR'},
        {'id': 'E3', 'data': 11.99},
        {'id': 'F3', 'data': 'Bedtime Originals Choo Choo Express Plush Elephant - Humphrey'},

        {'id': 'A4', 'data': datetime.datetime(2022, 9, 11, 0, 0)},
        {'id': 'B4', 'data': 'John Smith'},
        {'id': 'C4', 'data': '4273 9666 4581 5642'},
        {'id': 'D4', 'data': 'USD'},
        {'id': 'E4', 'data': 339.99},
        {'id': 'F4', 'data': 'Robot Vacuum Mary, Nobuk Robotic Vacuum Cleaner and Mop, 5000Pa Suction, Intelligent AI Mapping, Virtual Walls, Ideal for Pets Hair, Self-Charging, Carpets, Hard Floors, Tile, Wi-Fi, App Control'}
    ]

    assert exp == got


def test400_dump(fix_uuid):
    """Test object dump (to YAML)"""

    obj = mod.ExcelDocument(DATADIR / "table-example.xlsx")

    try:
        f = tempfile.NamedTemporaryFile(mode="wt", suffix=".yml", delete=False)
        obj.dump(f.name)
        got = load_yaml(f.name)
    finally:
        #print(f.name)
        Path(f.name).unlink()

    #import pprint; pprint.pprint(got)

    exp = load_yaml(DATADIR / "table-example.yml")
    assert exp == got


def test410_dump_ctx(fix_uuid):
    """Test object dump (to YAML)"""

    obj = mod.ExcelDocument(DATADIR / "table-example.xlsx")

    try:
        f = tempfile.NamedTemporaryFile(mode="wt", suffix=".yml", delete=False)
        obj.dump(f.name, context_fields=["column", "row"])
        got = load_yaml(f.name)
    finally:
        #print(f.name)
        Path(f.name).unlink()

    #import pprint; pprint.pprint(got)

    exp = load_yaml(DATADIR / "table-example-context.yml")
    assert exp == got
