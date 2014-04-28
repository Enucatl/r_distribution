"""Create a mask where the value is true for the thicker (most absorbing)
part of a rectangular sample.

- the 1d sobel filter is applied
- a 3-pixel gaussian filter is applied
- a non maximum filter is applied
- the image is hysteresis-thresholded

"""

import logging
import numpy as np
import scipy.ndimage as ndimage

import pypes.component

log = logging.getLogger(__name__)


class ThicknessFeatureSegmentation(pypes.component.Component):
    """
    mandatory input packet attributes:
    - data: an absorption dataset of a rectangular object

    optional input packet attributes:
    None

    parameters:
    - high_threshold: high threshold for the hysteresis-thresholding
      algorithm [default 0.004]
    - low_threshold: low threshold for the hysteresis-thresholding
      algorithm [default 0.001]

    output packet attributes:
    - mask: True where the interesting part is, False elsewhere

    """

    # defines the type of component we're creating.
    __metatype__ = 'TRANSFORMER'

    def __init__(self):
        # initialize parent class
        pypes.component.Component.__init__(self)

        # Setup any user parameters required by this component
        # 2nd arg is the default value, 3rd arg is optional list of choices
        self.set_parameter('high_threshold', 0.004)
        self.set_parameter('low_threshold', 0.001)

        # log successful initialization message
        log.debug('Component Initialized: %s', self.__class__.__name__)

    def run(self):
        """Run the detection algorithm"""
        # Define our components entry point
        while True:

            high_threshold = self.get_parameter('high_threshold')
            low_threshold = self.get_parameter('low_threshold')

            # for each packet waiting on our input port
            for packet in self.receive_all('in'):
                try:
                    image = packet.get("data")
                    log.debug("%s received %s %s",
                              self.__class__.__name__, image.shape, image)
                    edges = ndimage.sobel(
                        ndimage.gaussian_filter1d(
                            image,
                            sigma=3),
                        mode="constant")
                    non_maximum_suppressed = ndimage.maximum_filter1d(
                        edges, 1)
                    mask = np.zeros_like(non_maximum_suppressed)
                    for i, line in enumerate(non_maximum_suppressed):
                        hysteresis_thresholded = -ndimage.binary_dilation(
                            np.abs(line) > high_threshold,
                            iterations=-1,
                            mask=np.abs(line) > low_threshold)
                        features, feature_number = ndimage.measurements.label(
                            hysteresis_thresholded)
                        mask[i] = features == 1
                    packet.set("data", mask)
                except:
                    log.error('Component Failed: %s',
                              self.__class__.__name__, exc_info=True)

                # send the packet to the next component
                self.send('out', packet)

            # yield the CPU, allowing another component to run
            self.yield_ctrl()


class MinimumThresholdSegmentation(pypes.component.Component):
    """
    mandatory input packet attributes:
    - data: an absorption dataset of a rectangular object

    optional input packet attributes:
    None

    parameters:
    None

    output packet attributes:
    - mask: True where the interesting part is, False elsewhere

    """

    # defines the type of component we're creating.
    __metatype__ = 'TRANSFORMER'

    def __init__(self):
        # initialize parent class
        pypes.component.Component.__init__(self)

        # log successful initialization message
        log.debug('Component Initialized: %s', self.__class__.__name__)

    def run(self):
        """Run the detection algorithm"""
        # Define our components entry point
        while True:

            # for each packet waiting on our input port
            for packet in self.receive_all('in'):
                try:
                    image = packet.get("data")
                    log.debug("%s received %s %s",
                              self.__class__.__name__, image.shape, image)
                    mask = np.zeros_like(image, dtype=np.bool)
                    for i, line in enumerate(image):
                        minimum = np.min(image[i])
                        factor = 1.1
                        threshold = factor * minimum
                        mask[i] = image[i] < threshold
                    packet.set("data", mask)
                except:
                    log.error('Component Failed: %s',
                              self.__class__.__name__, exc_info=True)

                # send the packet to the next component
                self.send('out', packet)

            # yield the CPU, allowing another component to run
            self.yield_ctrl()
