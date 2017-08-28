import matplotlib.pyplot as plt
import numpy as np

from Scrpt_base import Scrpt_base
from Log import Log


class Plt(Scrpt_base):
    """Class 'Util' - contains basic utils (may be embedded in appropriate classes).
    To be embedded in others classes requiring such functionality."""

    # plt = matplotlib.pyplot

    default_settings = {}

    def __init__(self, log, user_settings=None):
        Scrpt_base.__init__(self, self.default_settings)
        self.update_settings(user_settings)
        self.log = log  # logger should be define outside

    def proxy(self, func, *args, **kwargs):
        """Proxy to call matplotlib.pyplot methods. Plus some custom functionality"""
        getattr(plt, func)(*args, **kwargs)

    def figure_setup(self, **kwargs):
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)

        if 'x_grid' in kwargs.keys():
            x_grid = kwargs['x_grid']
            if 3 == len(x_grid):
                ax.set_xticks(np.arange(x_grid[0], x_grid[1], x_grid[2]))
            elif 4 == len(x_grid):
                ax.set_xticks(np.arange(x_grid[0], x_grid[1], x_grid[2]))
                ax.set_xticks(np.arange(x_grid[0], x_grid[1], x_grid[3]), minor=True)

        if 'y_grid' in kwargs.keys():
            y_grid = kwargs['y_grid']
            if 3 == len(y_grid):
                ax.set_yticks(np.arange(y_grid[0], y_grid[1], y_grid[2]))
            elif 4 == len(y_grid):
                ax.set_yticks(np.arange(y_grid[0], y_grid[1], y_grid[2]))
                ax.set_yticks(np.arange(y_grid[0], y_grid[1], y_grid[3]), minor=True)

        ax.grid(which='both')
        ax.grid(which='minor', alpha=0.2)
        ax.grid(which='major', alpha=0.5)

    def plot_0(self, *args, **kwargs):
        plt.close('all')
        plt.plot(*args, **kwargs)
        plt.grid()
        plt.axis('auto')
        plt.show(block=False)

    def plot_0_blocked(self, *args, **kwargs):
        plt.close('all')
        plt.plot(*args, **kwargs)
        plt.grid()
        plt.axis('auto')
        plt.show(block=True)

    def lpf(self, x, delta=3):
        y = []
        for i in range(len(x)):
            if i >= delta:
                foo = sum(x[i - delta:i]) / delta
                y.append(foo)
            else:
                y.append(x[i])
        return y
