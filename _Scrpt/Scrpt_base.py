

class Scrpt_base(object):
    """Class "Scrpt_base" - base class, should be inherited by all Scrpt classes. Contains some basic stuff."""

    def __init__(self, settings=None):
        self.cfg = {}  # config, contain basic settings
        Scrpt_base.update_settings(self, settings)

    def update_settings(self, stn):
        for item in stn.keys():
            self.cfg[item] = stn[item]

    def make_list(self, item):
        if not type(item) in (list, tuple):
            item_list = [item, ]
        elif type(item) is tuple:
            item_list = []
            for item_i in item:
                item_list.append(item_i)
        else:
            item_list = item
        return item_list
