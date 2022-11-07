"""
Test the different chunking modes for reading plain text files
"""

from pathlib import Path

from unittest.mock import Mock
import pytest

import pii_data.types.document as docmod

import pii_preprocess.doc.text.load as mod


DATADIR = Path(__file__).parents[2] / "data" / "text" / "lang"


@pytest.fixture
def fix_uuid(monkeypatch):
    """
    Monkey-patch the document module to ensure a fixed uuid
    """
    mock_uuid = Mock()
    mock_uuid.uuid4 = Mock(return_value="00000-11111")
    monkeypatch.setattr(docmod, "uuid", mock_uuid)


# ----------------------------------------------------------------


def test100_lines(fix_uuid):
    """
    Split by lines
    """
    opt = {"mode": "line"}
    obj = mod.TextSrcDocument(DATADIR / "en-morus-rubra.txt",
                              chunk_options=opt)
    assert str(obj) == "<SrcDocument 00000-11111>"

    got = list(obj)
    assert len(got) == 109
    assert got[0].data == "MORUS RUBRA\n"


def test110_words(fix_uuid):
    """
    Split by word chunks
    """
    opt = {"mode": "word"}
    obj = mod.TextSrcDocument(DATADIR / "en-morus-rubra.txt",
                              chunk_options=opt)
    assert str(obj) == "<SrcDocument 00000-11111>"

    got = list(obj)
    assert len(got) == 10

    assert got[0].data == "MORUS RUBRA\nFrom Wikipedia, the free encyclopedia\nSpecies of tree\n\nMORUS RUBRA, commonly known as the RED MULBERRY, is a species of\nmulberry native to eastern and central North America. It is found from\nOntario, Minnesota, and Vermont south to southern Florida, and west as\nfar as southeastern South Dakota, Nebraska, Kansas, and central Texas.\nThere have been reports of isolated populations (very likely\nnaturalized) in New Mexico, Idaho, and British Columbia. ([2])\n\nCommon in the United States, it is listed as an endangered species in\nCanada,([3][4]) and is susceptible to hybridization with the invasive\nwhite mulberry (M. "


def test111_words_min(fix_uuid):
    """
    Split by word chunks, set min_words
    """
    opt = {"mode": "word", "max_words": 11}
    obj = mod.TextSrcDocument(DATADIR / "en-morus-rubra.txt",
                              chunk_options=opt)
    assert str(obj) == "<SrcDocument 00000-11111>"

    got = list(obj)
    assert len(got) == 90

    assert got[0].data == "MORUS RUBRA\nFrom Wikipedia, the free encyclopedia\nSpecies of tree\n\nMORUS "


def test120_paragraphs():
    """
    Split by paragraphs
    """
    opt = {"mode": "para"}
    obj = mod.TextSrcDocument(DATADIR / "en-morus-rubra.txt",
                              chunk_options=opt)
    got = list(obj)
    assert len(got) == 21

    assert got[0].data == "MORUS RUBRA\nFrom Wikipedia, the free encyclopedia\nSpecies of tree\n\n"


def test121_paragraphs_eos():
    """
    Split by paragraphs, use also eos marks
    """
    opt = {"mode": "para", "eos": True}
    obj = mod.TextSrcDocument(DATADIR / "en-morus-rubra.txt",
                              chunk_options=opt)
    got = list(obj)
    assert len(got) == 42

    assert got[0].data == "MORUS RUBRA\nFrom Wikipedia, the free encyclopedia\nSpecies of tree\n\n"


def test122_paragraphs_wmin():
    """
    Split by paragraphs, min words
    """
    opt = {"mode": "para", "min_words": 20}
    obj = mod.TextSrcDocument(DATADIR / "en-morus-rubra.txt",
                              chunk_options=opt)
    got = list(obj)

    assert len(got) == 13
    assert got[0].data == "MORUS RUBRA\nFrom Wikipedia, the free encyclopedia\nSpecies of tree\n\nMORUS RUBRA, commonly known as the RED MULBERRY, is a species of\nmulberry native to eastern and central North America. It is found from\nOntario, Minnesota, and Vermont south to southern Florida, and west as\nfar as southeastern South Dakota, Nebraska, Kansas, and central Texas.\nThere have been reports of isolated populations (very likely\nnaturalized) in New Mexico, Idaho, and British Columbia. ([2])\n\n"


def test123_paragraphs_wmax():
    """
    Split by paragraphs, max words
    """
    opt = {"mode": "para", "max_words": 20}
    obj = mod.TextSrcDocument(DATADIR / "en-morus-rubra.txt",
                              chunk_options=opt)
    got = list(obj)

    assert len(got) == 63
    assert got[1].data == "MORUS RUBRA, commonly known as the RED MULBERRY, is a species of\nmulberry native to eastern and central North America. "


def test124_paragraphs_wminmax():
    """
    Split by paragraphs, min & max words
    """
    opt = {"mode": "para", "min_words": 20, "max_words": 20}
    obj = mod.TextSrcDocument(DATADIR / "en-morus-rubra.txt",
                              chunk_options=opt)
    got = list(obj)

    assert len(got) == 61
    assert got[7].data == "Contents\n\n-   1 Description\n-   2 Ecology\n-   3 Uses\n-   4 References\n-   5 External links\n\n\nDescription\n\n"


def test130_single(fix_uuid):
    """
    Single chunk
    """
    opt = {"mode": "single"}
    obj = mod.TextSrcDocument(DATADIR / "en-morus-rubra.txt",
                              chunk_options=opt)
    assert str(obj) == "<SrcDocument 00000-11111>"

    got = list(obj)
    assert len(got) == 1
    with open(DATADIR / "en-morus-rubra.txt", encoding="utf-8") as f:
        exp = f.read()
    assert exp == got[0].data
