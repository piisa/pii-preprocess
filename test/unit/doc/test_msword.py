
from pathlib import Path
import tempfile
import json
from types import MappingProxyType

from unittest.mock import Mock
import pytest

from pii_data.helper.io import load_yaml
import pii_data.types.document as docmod

import pii_preprocess.doc.msoffice.msword as mod


DATADIR = Path(__file__).parents[2] / "data" / "msword"

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
    obj = mod.MsWordDocument(DATADIR / "example.docx")
    assert str(obj) == "<SrcDocument 00000-11111>"


def test110_header(fix_uuid):
    """Test object header"""
    obj = mod.MsWordDocument(DATADIR / "example.docx")
    meta = {"origin": "msword",
            "type": "tree",
            "title": "The PII data specification example",
            "author": "PII group",
            "category": "test documents",
            "id": "00000-11111",
            "date": "2022-08-02T17:37:00"}
    assert obj.metadata == {"document": meta}


def test120_iter_struct_seq():
    """Test struct iteration, sequence"""
    obj = mod.MsWordDocument(DATADIR / "example-headings.docx", tree=False)
    assert isinstance(obj, docmod.SequenceSrcDocument)
    exp = json.loads(readfile(DATADIR / "example-headings-flat.json"))
    got = list(obj.iter_struct())
    assert exp == got


def test121_iter_struct_tree():
    """Test struct iteration, tree"""
    obj = mod.MsWordDocument(DATADIR / "example-headings.docx")
    assert isinstance(obj, docmod.TreeSrcDocument)
    got = list(obj.iter_struct())

    exp = json.loads(readfile(DATADIR / "example-headings-tree.json"))
    assert len(exp) == len(got)
    for e, g in zip(exp, got):
        #print("", e, g, sep="\n")
        assert e == g


def test130_chunks_tree():
    """Test object creation, chunk iteration, tree"""
    obj = mod.MsWordDocument(DATADIR / "example-headings.docx", tree=True)
    got = list(obj)
    exp = [
        docmod.DocumentChunk("P1", "A document title\n\n", {"level": 0}),
        docmod.DocumentChunk("P2", "Small paragraph before the first heading.\n", {"level": 0}),
        docmod.DocumentChunk("P3", "1. The first chapter\n",
                             {'section': '1. The first chapter', "level": 0}),
        docmod.DocumentChunk("P4", "Some text.\n",
                             {'section': '1. The first chapter', "level": 1}),
        docmod.DocumentChunk("P5", "More text.\n",
                             {'section': '1. The first chapter', "level": 1}),
        docmod.DocumentChunk("P6", "2. The second chapter\n",
                             {'section': '2. The second chapter', "level": 0}),
        docmod.DocumentChunk("P7", "2.1 First section\n",
                             {'section': '2. The second chapter', "level": 1}),
        docmod.DocumentChunk("P8", "Something.\n\n",
                             {'section': '2. The second chapter', "level": 2}),
    ]
    #import json;print("\n".join(json.dumps(g.as_dict()) for g in got))

    # Check only the first chunks
    for n, e in enumerate(exp):
        #print("", e.as_dict(), got[n].as_dict(), sep="\n")
        assert got[n] == e


def test131_chunks_seq():
    """Test object creation, chunk iteration, sequence"""
    obj = mod.MsWordDocument(DATADIR / "example-headings.docx", tree=False)
    chunks = list(obj)
    exp = [
        docmod.DocumentChunk("P1", "A document title\n\n"),
        docmod.DocumentChunk("P2", "Small paragraph before the first heading.\n"),
        docmod.DocumentChunk("P3", "1. The first chapter\n"),
        docmod.DocumentChunk("P4", "Some text.\n"),
        docmod.DocumentChunk("P5", "More text.\n"),
        docmod.DocumentChunk("P6", "2. The second chapter\n"),
        docmod.DocumentChunk("P7", "2.1 First section\n"),
        docmod.DocumentChunk("P8", "Something.\n\n")
    ]
    for n, e in enumerate(exp):
        assert chunks[n] == e


def test140_chunks_tree_context(fix_uuid):
    """Test object creation, chunk iteration, context"""
    obj = mod.MsWordDocument(DATADIR / "example-headings.docx",
                             iter_options={"context": True})
    got = list(obj)

    basectx = MappingProxyType(
        {"id": "00000-11111",
         "origin": "msword",
         "type": "tree",
         "title": "The PII data specification example",
         "author": "PII group",
         "category": "test documents",
         "date": "2022-08-13T16:41:00"}
    )

    exp = [
        docmod.DocumentChunk(
            "P1", "A document title\n\n",
            context={
                "document": basectx,
                "after": "Small paragraph before the first heading.\n",
                "level": 0}
        ),

        docmod.DocumentChunk(
            "P2", "Small paragraph before the first heading.\n",
            context={
                "document": basectx,
                "before": "A document title\n\n",
                "after": "1. The first chapter\n",
                "level": 0}
        ),

        docmod.DocumentChunk(
            "P3", "1. The first chapter\n",
            context={
                "document": basectx,
                "section": "1. The first chapter",
                "before": "Small paragraph before the first heading.\n",
                "after": "Some text.\n",
                "level": 0}
        ),

        docmod.DocumentChunk(
            "P4", "Some text.\n",
            context={
                "document": basectx,
                "section": "1. The first chapter",
                "level": 1,
                "before": "1. The first chapter\n",
                "after": "More text.\n"}
        ),
    ]
    for n, e in enumerate(exp):
        #print("", e.as_dict(), got[n].as_dict(), sep="\n")
        assert e == got[n]


def test400_dump(fix_uuid):
    """Test object dump"""

    obj = mod.MsWordDocument(DATADIR / "example-headings.docx")

    try:
        f = tempfile.NamedTemporaryFile(mode="wt", suffix=".yml", delete=False)
        obj.dump(f.name)
        got = load_yaml(f.name)
    finally:
        #print(f.name)
        Path(f.name).unlink()

    exp = load_yaml(DATADIR / "example-headings.yml")
    assert exp == got
