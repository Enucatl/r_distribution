"""Save a json file with the absorption and dark field values in the images
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
                                    nargs=1,
                                    help="hdf5 files to analyze")
    args = commandline_parser.parse_args()

    input_file = args.files[0]
    hdf5_file = h5py.File(input_file)
    hdf5_group = hdf5_file[group]
    absorption_image = -np.log(hdf5_group["absorption"][...])
    visibility_reduction_image = -np.log(
        hdf5_group["visibility_reduction"][...])
    dictionary = {
        "image_name": os.path.splitext(os.path.basename(input_file))[0],
        "image_data": {
            "absorption": absorption_image.tolist(),
            "visibility_reduction": visibility_reduction_image.tolist(),
            "ratio": (visibility_reduction_image /
                      absorption_image).tolist(),
        }
    }
    hdf5_file.close()
    print(json.dumps(dictionary))
