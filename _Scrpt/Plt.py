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
        return getattr(plt, func)(*args, **kwargs)

    def add_subplot(self, fig, layout=111, **kwargs):
        if 'facecolor' in kwargs.keys():
            subplot = fig.add_subplot(layout, facecolor=kwargs['facecolor'])
        else:
            subplot = fig.add_subplot(layout)

        if 'x_grid' in kwargs.keys():
            x_grid = kwargs['x_grid']
            if 3 == len(x_grid):
                subplot.set_xticks(np.arange(x_grid[0], x_grid[1], x_grid[2]))
            elif 4 == len(x_grid):
                subplot.set_xticks(np.arange(x_grid[0], x_grid[1], x_grid[2]))
                subplot.set_xticks(np.arange(x_grid[0], x_grid[1], x_grid[3]), minor=True)
        if 'y_grid' in kwargs.keys():
            y_grid = kwargs['y_grid']
            if 3 == len(y_grid):
                subplot.set_yticks(np.arange(y_grid[0], y_grid[1], y_grid[2]))
            elif 4 == len(y_grid):
                subplot.set_yticks(np.arange(y_grid[0], y_grid[1], y_grid[2]))
                subplot.set_yticks(np.arange(y_grid[0], y_grid[1], y_grid[3]), minor=True)
        subplot.grid(which='both')
        subplot.grid(which='minor', alpha=0.2)
        subplot.grid(which='major', alpha=0.5)

        for item in ('title', 'xlabel', 'ylabel'):
            if item in kwargs.keys():
                self.proxy(item, kwargs[item])

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

    def lpf(self, x, window=3):
        y = []
        for i in range(len(x)):
            if i >= window:
                foo = sum(x[i + 1 - window:i + 1]) / len(x[i + 1 - window:i + 1])
                y.append(foo)
                # self.log.info('%f %f %d %d %d_' % (x[i], y[i], i, window, len(x[i - window:i])))
            else:
                foo = sum(x[0:i + 1]) / len(x[0:i + 1])
                y.append(foo)
                # self.log.info('%f %f %d %d %d' % (x[i], y[i], i, window, len(x[0:i + 1])))                
        return y
