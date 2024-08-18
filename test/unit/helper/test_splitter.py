"""
Test the paragraph splitter
"""

from pathlib import Path


import pii_preprocess.helper.splitter as mod


DATADIR = Path(__file__).parents[2] / "data" / "text" / "lang"

def _load_text(name: str) -> str:
    with open(DATADIR / name, encoding="utf-8") as f:
        return f.read()

def _print_para(it):
    for p in it:
        print(repr(p))

# ----------------------------------------------------------------


def test100_constructor():
    """
    Split by lines
    """
    sp = mod.ParagraphSplitter()
    assert str(sp) == "<ParagraphSplitter eop>"


def test200_eop():
    """
    Split by EOP
    """
    sp = mod.ParagraphSplitter()

    data = _load_text("en-morus-rubra.txt")
    got = list(sp(data))
    assert len(got) == 21
    assert got[:2] == [
        "MORUS RUBRA\nFrom Wikipedia, the free encyclopedia\nSpecies of tree\n\n",
        'MORUS RUBRA, commonly known as the RED MULBERRY, is a species of\nmulberry native to eastern and central North America. It is found from\nOntario, Minnesota, and Vermont south to southern Florida, and west as\nfar as southeastern South Dakota, Nebraska, Kansas, and central Texas.\nThere have been reports of isolated populations (very likely\nnaturalized) in New Mexico, Idaho, and British Columbia. ([2])\n\n'
    ]


def test210_eosn():
    """
    Split by EOSN
    """
    sp = mod.ParagraphSplitter("eosn")

    data = _load_text("en-morus-rubra.txt")
    got = list(sp(data))
    #_print_para(got)
    assert len(got) == 42
    assert got[:2] == [
        "MORUS RUBRA\nFrom Wikipedia, the free encyclopedia\nSpecies of tree\n\n",
        'MORUS RUBRA, commonly known as the RED MULBERRY, is a species of\nmulberry native to eastern and central North America. It is found from\nOntario, Minnesota, and Vermont south to southern Florida, and west as\nfar as southeastern South Dakota, Nebraska, Kansas, and central Texas.\n'
    ]


def test220_eos():
    """
    Split by EOS
    """
    sp = mod.ParagraphSplitter("eos")

    data = _load_text("en-morus-rubra.txt")
    got = list(sp(data))
    assert len(got) == 59
    assert got[:2] == [
        'MORUS RUBRA\nFrom Wikipedia, the free encyclopedia\nSpecies of tree\n\n',
        'MORUS RUBRA, commonly known as the RED MULBERRY, is a species of\nmulberry native to eastern and central North America. ']



def test300_wmin():
    """
    Split by paragraphs, min words
    """
    ps = mod.ParagraphSplitter(min_words=20)

    data = _load_text("en-morus-rubra.txt")
    got = list(ps(data))

    assert len(got) == 13
    assert got[0] == "MORUS RUBRA\nFrom Wikipedia, the free encyclopedia\nSpecies of tree\n\nMORUS RUBRA, commonly known as the RED MULBERRY, is a species of\nmulberry native to eastern and central North America. It is found from\nOntario, Minnesota, and Vermont south to southern Florida, and west as\nfar as southeastern South Dakota, Nebraska, Kansas, and central Texas.\nThere have been reports of isolated populations (very likely\nnaturalized) in New Mexico, Idaho, and British Columbia. ([2])\n\n"


def test310_wmax():
    """
    Split by paragraphs, max words
    """
    ps = mod.ParagraphSplitter(max_words=20)

    data = _load_text("en-morus-rubra.txt")
    got = list(ps(data))

    assert len(got) == 63
    assert got[1] == "MORUS RUBRA, commonly known as the RED MULBERRY, is a species of\nmulberry native to eastern and central North America. "


def test320_wminmax():
    """
    Split by paragraphs, min & max words
    """
    ps = mod.ParagraphSplitter(min_words=20, max_words=20)

    data = _load_text("en-morus-rubra.txt")
    got = list(ps(data))

    assert len(got) == 61
    assert got[7] == "Contents\n\n-   1 Description\n-   2 Ecology\n-   3 Uses\n-   4 References\n-   5 External links\n\n\nDescription\n\n"
