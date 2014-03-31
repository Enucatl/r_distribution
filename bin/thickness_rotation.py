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
    reader = Hdf5Reader()
    reader.__metatype__ = "TRANSFORMER"
    out = NMFunction(n=1, m=m)
    network = {
        reader: {
            out: ("out", "in")
        }
    }
    return network


def average_function(a, w):
    "average over last axis"
    print("SHAPES", a.shape, w.shape)
    return np.average(a, axis=-1, weights=w)


def average():
    "calculate weighted average"
    average = NMFunction(n=2)
    average.set_parameter(
        "function", average_function)
    return average


def datasets(*_):
    "return the name of the datasets"
    return [
        "postprocessing/absorption",
        "postprocessing/visibility_reduction"]


def log_function(df, a):
    "logarithm ratio"
    return np.log(df)/np.log(a)


def main(file_name, jobs):
    in1out2 = NMFunction(n=1, m=2)
    in1out2.__metatype__ = "ADAPTER"
    in1out2.set_parameter("function", datasets)
    abs_reader = HigherOrderComponent(multiple_outputs_reader(m=3))
    df_reader = HigherOrderComponent(multiple_outputs_reader(m=2))
    feature_segmentation = ThicknessFeatureSegmentation()
    feature_segmentation_out = NMFunction(m=3)
    log_ratio = NMFunction(n=2)
    log_ratio.set_parameter(
        "function",
        log_function)
    average_abs = average()
    average_df = average()
    average_r = average()
    network = {
        in1out2: {
            abs_reader: ("out", "in"),
            df_reader: ("out1", "in"),
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
        feature_segmentation: {
            feature_segmentation_out: ("out", "in")
        },
        log_ratio: {
            average_r: ("out", "in")
        },
        feature_segmentation_out: {
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
