import datetime


class Scrpt_base(object):
    """Class "Scrpt_base" - base class, should be inherited by all Scrpt classes. Contains some basic stuff."""

    def __init__(self, settings=None):
        self.cfg = {}  # config, contain basic settings
        Scrpt_base.setup(self, settings)

    def setup(self, settings=None):
        """ add/upda settings to config"""
        if settings and type(settings) is dict:
            for key in settings.keys():
                self.cfg[key] = settings[key]

    def get_time(self):
        """ Get system date/time in different formats"""
        weekday = ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday')
        month = ('Dummy', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December')

        foo = {}

        now = datetime.datetime.now().replace(microsecond=0)
        foo['now'] = now

        foo['month'] = month[now.month]
        foo['week_num'] = datetime.date(now.year, now.month, now.day).isocalendar()[1]
        foo['week_day'] = weekday[datetime.date(now.year, now.month, now.day).weekday()]

        foo['time'] = '%02d:%02d:%02d' % (now.hour, now.minute, now.second)
        foo['date'] = '%04d/%02d/%02d' % (now.year, now.month, now.day)
        foo['date_time'] = '%04d/%02d/%02d  %02d:%02d:%02d' % (now.year, now.month, now.day, now.hour, now.minute, now.second)
        foo['date_time_tag'] = '%04dy%02dm%02dd_%02dh%02dm%02ds' % (now.year, now.month, now.day, now.hour, now.minute, now.second)
        foo['date_time_wo_year_tag'] = '%02dm%02dd_%02dh%02dm%02ds' % (now.month, now.day, now.hour, now.minute, now.second)
        foo['date_time_wo_year_sec_tag'] = '%02dm%02dd_%02dh%02dm' % (now.month, now.day, now.hour, now.minute)

        return foo

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
