"""Calculate average df, abs, ratio values for each line."""

import numpy as np

import logging
import logging.config
from r_distribution.logger_config import config_dictionary
from r_distribution.basic_parser import BasicParser
log = logging.getLogger()

import pypes.pipeline
import pypes.packet
from pypes.component import HigherOrderComponent

from pypes.plugins.hdf5 import Hdf5Reader
from pypes.plugins.nm_function import NMFunction
from r_distribution.feature_segmentation import ThicknessFeatureSegmentation


def multiple_outputs_reader(m=2):
    "repeat the output of the reader m times"
    abs_reader_reader = Hdf5Reader()
    abs_reader_out = NMFunction(n=1, m=m)
    abs_reader_network = {
        abs_reader_reader: {
            abs_reader_out: ("out", "in")
        }
    }
    return abs_reader_network


def weighted_average():
    "calculate weighted average"
    weighted_average = NMFunction(n=2)
    weighted_average.set_parameter(
        "function", lambda a, w: np.average(a, axis=-1, weights=w))
    return weighted_average


def datasets(*args):
    "return the name of the datasets"
    return [
        "postprocessing/absorption",
        "postprocessing/visibility_reduction",
        "postprocessing/visibility"]


def main(file_name, jobs):
    in1out3 = NMFunction(n=1, m=3)
    in1out3.set_parameter("function", datasets)
    abs_reader = HigherOrderComponent(multiple_outputs_reader(m=3))
    df_reader = HigherOrderComponent(multiple_outputs_reader(m=2))
    visibility_reader = Hdf5Reader()
    squared = NMFunction()
    squared.set_parameter("function", np.square)
    feature_segmentation = ThicknessFeatureSegmentation()
    product = NMFunction(n=2, m=3)
    product.set_parameter("function", lambda x, y: x * y)
    log_ratio = NMFunction(n=2)
    log_ratio.set_parameter(
        "function",
        lambda df, a: np.log(df)/np.log(a))
    average_abs = weighted_average()
    average_df = weighted_average()
    average_r = weighted_average()
    network = {
        in1out3: {
            abs_reader: ("out", "in"),
            df_reader: ("out1", "in"),
            visibility_reader: ("out2", "in")
        },
        abs_reader: {
            average_abs: ("out", "in"),
            feature_segmentation: ("out1", "in"),
            log_ratio: ("out2", "in1")
        },
        df_reader: {
            log_ratio: ("out", "in"),
            average_df: ("out1", "in")
        },
        visibility_reader: {
            squared: ("out", "in")
        },
        feature_segmentation: {
            product: ("out", "in")
        },
        squared: {
            product: ("out", "in1")
        },
        product: {
            average_abs: ("out", "in1"),
            average_df: ("out1", "in1"),
            average_r: ("out2", "in1")
        },
    }
    pipeline = pypes.pipeline.Dataflow(network, n=jobs)
    packet = pypes.packet.Packet()
    packet.set("file_name", file_name)
    pipeline.send(packet)
    pipeline.close()


if __name__ == '__main__':
    commandline_parser = BasicParser()
    args = commandline_parser.parse_args()
    if args.verbose:
        config_dictionary['handlers']['default']['level'] = 'DEBUG'
        config_dictionary['loggers']['']['level'] = 'DEBUG'
    logging.config.dictConfig(config_dictionary)
    main(args.file[0], args.jobs)
