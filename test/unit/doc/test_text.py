
from pathlib import Path
import tempfile
import json
from types import MappingProxyType

from unittest.mock import Mock
import pytest

from pii_data.helper.io import load_yaml
import pii_data.types.document as docmod

import pii_preprocess.doc.text.load as mod


DATADIR = Path(__file__).parents[2] / "data" / "text"

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
    import pii_preprocess.doc.text.read.base as modbase
    mock_st = Mock()
    mock_st.st_mtime = 10
    mock_os = Mock()
    mock_os.stat = Mock(return_value=mock_st)
    monkeypatch.setattr(modbase, "os", mock_os)


# ----------------------------------------------------------------


def test100_constructor(fix_uuid):
    """Test object creation"""
    obj = mod.TextSrcDocument(DATADIR / "doc-example.txt")
    assert str(obj) == "<SrcDocument 00000-11111>"


def test110_header(fix_uuid):
    """Test object header"""
    meta = {"document": {"title": "one example", "id": "abcd"}}
    obj = mod.TextSrcDocument(DATADIR / "doc-example.txt", metadata=meta)
    assert str(obj) == "<SrcDocument abcd>"

    exp = MappingProxyType({**meta["document"], "origin": "text", "type": "sequence"})
    assert obj.metadata == {"document": exp}


def test120_struct_iter_seq():
    """Test struct iteration, sequence"""
    obj = mod.TextSrcDocument(DATADIR / "doc-example.txt")
    assert isinstance(obj, docmod.SequenceSrcDocument)

    with open(DATADIR / "doc-example.txt", encoding="utf-8") as f:
        lines = list(f)
    exp = [{"id": f"{n}", "data": ln} for n, ln in enumerate(lines, start=1)]

    got = list(obj.iter_struct())
    assert exp == got


def test121_struct_iter_tree():
    """Test struct iteration, tree"""
    opt = {"mode": "tree"}
    obj = mod.TextSrcDocument(DATADIR / "doc-example.txt", chunk_options=opt)
    assert isinstance(obj, docmod.TreeSrcDocument)

    got = list(obj.iter_struct())
    #import json; print(json.dumps(got, indent=2, ensure_ascii=False))
    exp = json.loads(readfile(DATADIR / "doc-example.json"))
    assert exp == got


def test130_full_iter():
    """Test full iteration"""
    obj = mod.TextSrcDocument(DATADIR / "doc-example.txt")
    got = list(obj)

    with open(DATADIR / "doc-example.txt", encoding="utf-8") as f:
        lines = list(f)
    exp = [
        docmod.DocumentChunk(str(n), ln) for n, ln in enumerate(lines, start=1)
    ]
    assert exp == got


def test131_full_iter():
    """Test full iteration, tree"""
    opt = {"mode": "tree"}
    obj = mod.TextSrcDocument(DATADIR / "doc-example.txt", chunk_options=opt)
    got = list(obj)
    #import json; print(json.dumps(got, indent=2, ensure_ascii=False))

    elem = json.loads(readfile(DATADIR / "doc-example-full-tree.json"))
    exp = [docmod.DocumentChunk(*e) for e in elem]

    for n, e in enumerate(exp):
        #print("", e.as_dict(), got[n].as_dict(), sep="\n")
        assert e == got[n]
    assert exp == got


def test140_chunks_context(fix_uuid, fix_tstamp):
    """Test object creation, chunk iteration, context"""
    obj = mod.TextSrcDocument(DATADIR / "doc-example.txt",
                              iter_options={"context": True})
    got = list(obj)

    #for e in got:
    #    del e.context["document"]
    #import json; print(json.dumps(got, indent=2, ensure_ascii=False))

    docmeta = MappingProxyType(
        {"id": "00000-11111", "origin": "text", "type": "sequence",
         "date": "1970-01-01T00:00:10"}
    )
    elem = json.loads(readfile(DATADIR / "doc-example-full-ctx.json"))
    exp = [docmod.DocumentChunk(e[0], e[1], {**e[2], "document": docmeta})
           for e in elem]
    for e, g in zip(exp, got):
        assert g == e


def test400_dump(fix_uuid, fix_tstamp):
    """Test object dump"""

    opt = {"mode": "tree"}
    obj = mod.TextSrcDocument(DATADIR / "doc-example.txt", chunk_options=opt)

    try:
        f = tempfile.NamedTemporaryFile(mode="wt", suffix=".yml", delete=False)
        obj.dump(f.name)
        got = load_yaml(f.name)
    finally:
        #print(f.name)
        Path(f.name).unlink()

    exp = load_yaml(DATADIR / "doc-example-tree.yml")
    assert exp == got
