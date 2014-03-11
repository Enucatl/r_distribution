"""Save a json file with the visibility, absorption, dark field and ratio
values in the images

"""

import h5py
import numpy as np
import argparse
import json
import os

import matplotlib.pyplot as plt
import scipy.ndimage as ndimage

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
    absorption_image = (hdf5_group["absorption"][...])
    visibility_reduction_image = -np.log(
        hdf5_group["visibility_reduction"][...])
    visibility = hdf5_group["visibility"][...]
    line = absorption_image[1, ...]
    edges = ndimage.sobel(
        ndimage.gaussian_filter(line, 3),
        mode='constant')[1:-1]
    print(absorption_image.shape)
    _, ((hist1, hist2),
        (hist3, hist4),
        (hist5, hist6)) = plt.subplots(3, 2)
    hist1.hist(
        range(line.shape[0]),
        bins=line.shape[0],
        weights=line,
    )
    hist2.hist(
        range(edges.shape[0]),
        bins=edges.shape[0],
        weights=edges,
    )
    non_maximum_suppression = ndimage.maximum_filter1d(edges, 1)
    hist3.hist(
        range(non_maximum_suppression.shape[0]),
        bins=non_maximum_suppression.shape[0],
        weights=non_maximum_suppression,
    )
    high_threshold = 0.004
    low_threshold = 0.001
    hysteresis_thresholded = -ndimage.binary_dilation(
        (np.abs(non_maximum_suppression) > high_threshold),
        iterations=-1,
        mask=(np.abs(non_maximum_suppression) > low_threshold))
    hist4.hist(
        range(hysteresis_thresholded.shape[0]),
        bins=hysteresis_thresholded.shape[0],
        weights=hysteresis_thresholded * line[1:-1],
    )
    features, feature_number = ndimage.measurements.label(
        hysteresis_thresholded)
    print(features, feature_number)
    if feature_number == 2 or feature_number == 3:
        final_image = np.where(features == 2, line[1:-1], 0)
    elif feature_number == 1:
        final_image = line[1:-1]
    else:
        print("features", feature_number, "found!!!")
    hist5.hist(
        range(final_image.shape[0]),
        bins=final_image.shape[0],
        weights=final_image,
    )
    plt.show()
    dictionary = {
        "image_name": os.path.splitext(os.path.basename(input_file))[0],
        "image_data": {
            "absorption": absorption_image.tolist(),
            "visibility_reduction": visibility_reduction_image.tolist(),
            "visibility": visibility.tolist(),
            "ratio": (visibility_reduction_image /
                      absorption_image).tolist(),
        }
    }
    hdf5_file.close()
    print(json.dumps(dictionary))
