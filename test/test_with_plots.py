"""Create a mask where the value is true for the thicker (most absorbing)
part of a rectangular sample.

- the 1d sobel filter is applied
- a 3-pixel gaussian filter is applied
- a non maximum filter is applied
- the image is hysteresis-thresholded

"""

import numpy as np
import h5py
import scipy.ndimage as ndimage
import matplotlib.pyplot as plt
import argparse

parser = argparse.ArgumentParser(__doc__)
parser.add_argument("index", type=int,
                    nargs='?',
                    default=0)

args = parser.parse_args()
index = args.index
h5py_file = h5py.File("../data/S00918_S00957.hdf5")
dataset = h5py_file["postprocessing/absorption"][...]
image = dataset
_, ((fig1, fig2), (fig3, fig4), (fig5, fig6)) = plt.subplots(3, 2)
fig1.plot(image[index])
derivative_filter = ndimage.gaussian_filter1d(
    image,
    order=1,
    sigma=10)[..., 1:-1]
fig2.plot(derivative_filter[index])
edges = ndimage.sobel(derivative_filter, mode="constant")
fig3.plot(edges[index])
non_maximum_suppressed = ndimage.maximum_filter1d(
    edges, 3)
high_threshold = np.max(non_maximum_suppressed[index]) * 0.7
low_threshold = high_threshold * 0.4
print(high_threshold, low_threshold)
fig4.plot(np.abs(non_maximum_suppressed[index]))
mask = np.zeros_like(non_maximum_suppressed)
for i, line in enumerate(non_maximum_suppressed):
    hysteresis_thresholded = -ndimage.binary_dilation(
        np.abs(line) > high_threshold,
        iterations=-1,
        mask=np.abs(line) > low_threshold)
    features, feature_number = ndimage.measurements.label(
        hysteresis_thresholded)
    print(feature_number)
    if feature_number == 3:
        mask[i] = features == 2
    elif feature_number == 1:
        mask[i] = features == 1
    elif feature_number == 2:
        mask[i] = features == 2

fig5.plot(mask[index])
min_mask = np.zeros_like(image, dtype=np.bool)
for i, line in enumerate(image):
    minimum = np.min(image[i])
    factor = 1.1
    threshold = factor * minimum
    min_mask[i] = image[i] < threshold
fig6.plot(min_mask[index])
plt.show()
plt.ion()
input()
