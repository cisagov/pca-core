"""pca/config/config.py ."""


# Standard Python Libraries
import os
import sys

# Third-Party Libraries
import yaml

CONFIG_FILENAME = os.path.expanduser("/etc/pca/pca.yml")
DEFAULT_SECTION = "default-section"
PRODUCTION_SECTION = "production"
TESTING_SECTION = "testing"
DATABASE_NAME = "database-name"
DATABASE_URI = "database-uri"
TESTING_DATABASE_NAME = "test_pca"
PRODUCTION_DATABASE_NAME = "pca"
DEFAULT_DATABASE_URI = "mongodb://localhost:27017/"


class Config(object):
    """Configuration class."""

    def __init__(self, config_section=None):
        """Initialize object."""
        if not os.path.exists(CONFIG_FILENAME):
            print(
                'Configuration file not found: "%s"' % CONFIG_FILENAME, file=sys.stderr
            )
            self.__write_config()
            print("A default configuration file was created.", file=sys.stderr)
        config = self.__read_config()
        if config_section is None:
            config_section = config.get(DEFAULT_SECTION)
        self.active_section = config_section
        self.db_name = config[config_section].get(DATABASE_NAME)
        self.db_uri = config[config_section].get(DATABASE_URI)

    def __read_config(self):
        """Load configuration from file."""
        config_file = open(CONFIG_FILENAME, "r")
        config = yaml.safe_load(config_file)
        config_file.close()
        return config

    def __write_config(self):
        """Write configuration to file."""
        config = dict()
        config[DEFAULT_SECTION] = TESTING_SECTION
        config[TESTING_SECTION] = {
            DATABASE_URI: DEFAULT_DATABASE_URI,
            DATABASE_NAME: TESTING_DATABASE_NAME,
        }
        config[PRODUCTION_SECTION] = {
            DATABASE_URI: DEFAULT_DATABASE_URI,
            DATABASE_NAME: PRODUCTION_DATABASE_NAME,
        }
        with open(CONFIG_FILENAME, "wb") as config_file:
            config_file.write(
                yaml.dump(config, encoding=("utf-8"), default_flow_style=False)
            )
