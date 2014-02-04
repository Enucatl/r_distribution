"""Save a json file with the absorption and dark field values in the pixels
of all images

"""

import h5py
import numpy as np
import argparse
import json
import os

group = "postprocessing"

if __name__ == '__main__':

    commandline_parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    commandline_parser.add_argument('files',
                                    nargs='+',
                                    help="hdf5 files to analyze")
    args = commandline_parser.parse_args()

    input_files = args.files
    pixels = []
    for input_file in input_files:
        hdf5_file = h5py.File(input_file)
        hdf5_group = hdf5_file[group]
        absorption_image = np.ravel(hdf5_group["absorption"])
        visibility_reduction_image = np.ravel(
            hdf5_group["visibility_reduction"])
        for absorption, visibility_reduction in zip(
                absorption_image, visibility_reduction_image):
            ratio = visibility_reduction / absorption
            dictionary = {
                "image": os.path.splitext(os.path.basename(input_file))[0],
                "absorption": absorption,
                "visibility_reduction": visibility_reduction,
                "ratio": ratio,
            }
            pixels.append(dictionary)
        hdf5_file.close()
    print(json.dumps(pixels))
