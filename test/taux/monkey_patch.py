
from pathlib import Path

from unittest.mock import Mock

from pii_data.helper.config import load_single_config
import pii_data.types.doc.document as docmod

from pii_preprocess.defs import FMT_CONFIG_LOADER, PII_PREPROCESS_PLUGIN_ID
import pii_preprocess.loader.utils as modutils


DATADIR = Path(__file__).parents[1] / "data"


class MockPlugin:

    def __init__(self, config, debug, **kwargs):
        pass

    def get_priority(self):
        return 100

    def get_config(self):
        cfgfile = DATADIR / "config" / "test-loader-plugin.json"
        return load_single_config(cfgfile, FMT_CONFIG_LOADER)



def patch_entry_points(monkeypatch):
    """
    Monkey-patch the importlib.metadata.entry_points call to return only our
    plugin entry point
    """
    mock_entry = Mock()
    mock_entry.name = "pii-preprocessor-plg [unit-test]"
    mock_entry.load = Mock(return_value=MockPlugin)

    mock_ep = Mock(return_value={PII_PREPROCESS_PLUGIN_ID: [mock_entry]})
    monkeypatch.setattr(modutils, 'entry_points', mock_ep)


def patch_uuid(monkeypatch):
    """
    Monkey-patch the document module to ensure a fixed uuid
    """
    mock_uuid = Mock()
    mock_uuid.uuid4 = Mock(return_value="11111-22222")
    monkeypatch.setattr(docmod, "uuid", mock_uuid)
