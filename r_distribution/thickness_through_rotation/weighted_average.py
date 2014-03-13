"""Weighted average along given axis"""

import numpy as np
import logging

import pypes.component

log = logging.getLogger(__name__)


class WeightedAverage(pypes.component.Component):
    """
    mandatory input packet attributes:
    - data: the data to average
    - weights: the weights

    optional input packet attributes:
    None

    parameters:
    - axis: [default: None]

    output packet attributes:
    - data: the averaged data

    """

    # defines the type of component we're creating.
    __metatype__ = 'TRANSFORMER'

    def __init__(self):
        # initialize parent class
        pypes.component.Component.__init__(self)

        # Setup any user parameters required by this component
        # 2nd arg is the default value, 3rd arg is optional list of choices
        self.set_parameter('axis', None)

        # log successful initialization message
        log.debug('Component Initialized: %s', self.__class__.__name__)

    def run(self):
        "Average along axis"
        # Define our components entry point
        while True:

            # myparam = self.get_parameter('MyParam')

            # for each packet waiting on our input port
            for packet in self.receive_all('in'):
                try:
                    data = packet.get("data")
                    weights = packet.get("weights")
                    averaged = np.average(
                        data,
                        axis=self.get_parameter("axis"),
                        weights=weights)
                    packet.set("data", averaged)
                except:
                    log.error('Component Failed: %s',
                              self.__class__.__name__, exc_info=True)

                # send the packet to the next component
                self.send('out', packet)

            # yield the CPU, allowing another component to run
            self.yield_ctrl()
