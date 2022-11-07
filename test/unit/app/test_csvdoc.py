from pathlib import Path
import tempfile

from unittest.mock import Mock
import pytest

from pii_data.helper import load_yaml
import pii_data.types.document as docmod
import pii_preprocess.app.csvdoc as mod


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
    monkeypatch.setattr(docmod, 'uuid', mock_uuid)


@pytest.fixture
def fix_tstamp(monkeypatch):
    """
    Monkey-patch the file modification time call
    """
    import pii_preprocess.doc.csv as modbase
    mock_st = Mock()
    mock_st.st_mtime = 20
    mock_os = Mock()
    mock_os.stat = Mock(return_value=mock_st)
    monkeypatch.setattr(modbase, "os", mock_os)


# -----------------------------------------------------------------------


def test10_read(fix_uuid, fix_tstamp):
    """Test reading a raw csv file"""

    with tempfile.NamedTemporaryFile(suffix=".yml") as f:
        f.close()

        mod.from_csv(fname('table-example.csv'), f.name, header=True,
                     id_path_prefix=False)
        #mod.from_raw(fname('doc-example.txt'), fname('doc-example-2.yaml'), 2)
        got = load_yaml(f.name)

        exp = load_yaml(fname('table-example.yml'))
        assert got == exp


def test20_write():
    """Test writing a csv file"""

    with tempfile.NamedTemporaryFile() as f:
        f.close()

        mod.to_csv(fname('table-example.yml'), f.name, header=True)
        #mod.from_raw(fname('doc-example.txt'), fname('doc-example-2.yaml'), 2)

        exp = readfile(fname('table-example.csv'))
        got = readfile(f.name)
        assert got == exp
