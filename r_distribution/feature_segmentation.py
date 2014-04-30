"""Create a mask where the value is true for the thicker (most absorbing)
part of a rectangular sample.

"""

import logging
import numpy as np

import pypes.component

log = logging.getLogger(__name__)


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
