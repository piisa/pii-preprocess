"""
Some utility functions to fetch configurations for pii-preprocess Loaders
"""

from pathlib import Path
from operator import itemgetter
from importlib.metadata import entry_points

from typing import Dict, List

from pii_data.helper.exception import ProcException
from pii_data.helper.config import load_config, merge_config, TYPE_CONFIG_LIST

from .. import defs


def get_plugin_config(config: Dict, debug: bool = False) -> List[Dict]:
    """
    Get all Loader configurations provided by pii-preprocess plugins
     :param config: a Loader base config, used to fetch specific config for
        loading plugins
     :param debug: debug parameter to pass to plugin loader classes
     :return: a list of Loader configs, as {section: config} in priority order
        (higher priority last)

    An instantiated plugin class must provide two methods: get_priority() and
    get_config()
    """

    # Configuration for plugins
    plugin_load_cfg = config.get("plugins", {}) if config else {}

    plugin_list = []

    for entry in entry_points().get(defs.PII_PREPROCESS_PLUGIN_ID, []):

        # See if we have specific options to load this plugin
        cfg = plugin_load_cfg.get(entry.name, {})
        if not cfg.get("load", True):
            continue        # plugin is not to be loaded
        options = cfg.get("options", {})

        # Load the plugin function
        plugin_class = entry.load()

        # Instantiate it
        try:
            plg = plugin_class(config=config, **options, debug=debug)
            plugin_list.append((plg.get_priority(), plg.get_config()))
        except Exception as e:
            raise ProcException("cannot instantiate plugin '{}': {}",
                                entry.name, e) from e

    return [{defs.FMT_CONFIG_LOADER: v[1]}
            for v in sorted(plugin_list, key=itemgetter(0))]


def get_loader_config(config: TYPE_CONFIG_LIST = None,
                      debug: bool = None) -> Dict:
    """
    Get the configuration for a pii-preprocessor Loader
     :param config: list of configurations to add on top of the system config
       (either filenames to load, or already loaded configs)
     :param debug: print out debug information
     :return: a dict holding a Loader config

    It will merge:
      - default Loader config (in package resources)
      - configs provided by pii-preprocess plugins
      - configurations passed in the `config` arguments
    """
    # Load base config
    base = Path(__file__).parents[1] / "resources" / defs.DEFAULT_CONFIG_LOADER
    base_config = load_config(base, defs.FMT_CONFIG_LOADER)

    # Add config from arguments
    if config:
        extra_config = load_config(config, defs.FMT_CONFIG_LOADER)
        full_config = merge_config([base_config] + [extra_config])
    else:
        extra_config = []
        full_config = base_config

    # See if we have config from plugins
    plugin_config = get_plugin_config(full_config, debug=debug)
    if plugin_config:
        # Construct the full loader config
        loader_config = [base_config] + plugin_config + [extra_config]
        # Merge all configs
        full_config = merge_config(loader_config)

    return full_config.get(defs.FMT_CONFIG_LOADER, {})
