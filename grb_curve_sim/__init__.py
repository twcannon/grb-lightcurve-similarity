import os.path

try:
    from configparser import ConfigParser
except ImportError:
    from configparser import SafeConfigParser as ConfigParser

grb_config = ConfigParser()
DEFAULT_CONFIG_FILES = []

LOCAL_CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "grb_curve_sim.conf")

print(f'Local Config: {LOCAL_CONFIG_PATH}')

grb_config.read(DEFAULT_CONFIG_FILES + [LOCAL_CONFIG_PATH])
