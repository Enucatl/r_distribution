"""Calculate average df, abs, ratio values for each line."""

import argparse

import numpy as np

import logging
import logging.config
from dpc_reconstruction.logger_config import config_dictionary
log = logging.getLogger()

import pypes.pipeline
import pypes.packet

from pypes.plugins.nm_function import NMFunction

def main(file_name):
    """@todo: Docstring for main.

    :file_name: @todo
    :returns: @todo

    """
    pass

if __name__ == '__main__':
    args = commandline_parser.parse_args()
    if args.verbose:
        config_dictionary['handlers']['default']['level'] = 'DEBUG'
        config_dictionary['loggers']['']['level'] = 'DEBUG'
    logging.config.dictConfig(config_dictionary)
    main(args.file)
