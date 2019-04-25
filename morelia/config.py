"""
Configuration
-------------
"""

import os
from configparser import NoOptionError, NoSectionError, SafeConfigParser
from pathlib import Path

import toml

from morelia.matchers import MethodNameStepMatcher, ParseStepMatcher, RegexpStepMatcher

DEFAULT_CONFIG_FILES = [".moreliarc", "~/.moreliarc", "/etc/morelia.rc"]


def expand_all(path):
    """Expand path."""
    return os.path.abspath(os.path.expandvars(os.path.expanduser(path)))


class Config:
    """Configuration object.

    Configuration is read from ini-style files and environment variables
    prefixed with `MORELIA_`.
    By default Morelia search for files:

        * .moreliarc
        * ~/.moreliarc
        * /etc/morelia.rc
    """

    def __init__(self, config_files=None, config_parser_class=None):
        self._env_prefix = "MORELIA_"
        self._items = {
            "tags": None,
            "formatter": None,
            "matchers": None,
            "show_all_missing": False,
        }
        if config_files is None:
            config_files = DEFAULT_CONFIG_FILES
        self._default_section = "morelia"
        self._config_files = [expand_all(config_file) for config_file in config_files]
        if config_parser_class is None:
            config_parser_class = SafeConfigParser
        self._config_parser_class = config_parser_class

    def load(self):
        """Load configuration."""
        self._update_from_file()
        self._update_from_environ()

    def _update_from_file(self):
        """Update config on settings from *.ini file."""
        config_parser = self._config_parser_class()
        config_parser.read(self._config_files)
        for key in self._items.keys():
            try:
                value = config_parser.get("morelia", key)
            except (NoOptionError, NoSectionError):
                pass
            else:
                self._items[key] = value

    def _update_from_environ(self):
        """Update config on environment variables."""
        for key in self._items.keys():
            try:
                value = os.environ[self._env_prefix + key.upper()]
            except KeyError:
                pass
            else:
                self._items[key] = value

    def get_tags_pattern(self):
        """Return tags pattern."""
        tags = self._items.get("tags", "")
        return tags if tags is not None else ""


def get_config(_memo={}):
    """Return config object."""
    try:
        return _memo["config"]
    except KeyError:
        config = Config()
        config.load()
        _memo["config"] = config
    return _memo["config"]


MATCHERS = {
    "parse": ParseStepMatcher,
    "regex": RegexpStepMatcher,
    "method": MethodNameStepMatcher,
}


class TOMLConfig:
    def __init__(self, section="default"):
        self.__section = section
        paths = (Path("pyproject.toml"), Path("~/.config/morelia/morelia.toml"))
        paths = [path for path in paths if path.exists()]
        self.__data = {"wip": False, "matchers": ["regex", "parse", "method"]}
        data = toml.load(paths).get("tool", {}).get("morelia", {}).get(section, {})
        self.__data.update(data)

    def get_matchers(self):
        return [MATCHERS[matcher] for matcher in self.__data["matchers"]]

    def get_writers(self):
        return []

    def __getitem__(self, key):
        return self.__data[key]
