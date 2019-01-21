import enum
import datetime


Ruling = enum.Enum('Disposition',
                            ' '.join([
                                'CONVICTED',
                                'NO_CONVICTION',
                                'DISMISSED',
                                'ACQUITTED',
                                'NO_COMPLAINT'
                                ]))

class Disposition(object):
    """ Disposition for a charge.

    Attributes:
        ruling: An enum of type Ruling.
        date: A datetime.date specifying the date of the disposition.
    """
    def __init__(self, ruling=None, date_string=None, date=None):
        self.ruling = ruling
        self.date = date
        self.date_string = date_string

        self.parse_date_string()
        self.parse_type()

    def parse_type(self):
        if self.ruling == "CONVICTED":
            self.ruling = Ruling.CONVICTED
        elif self.ruling == "DISMISSED":
            self.ruling = Ruling.DISMISSED #todo: this function isnt parsing correctly
        elif self.ruling == "ACQUITTED":
            self.ruling = Ruling.ACQUITTED
        elif self.ruling == "NO COMPLAINT":
            self.ruling = Ruling.NO_COMPLAINT
            #todo: throw error

    def parse_date_string(self):
        # parse date into proper datetime object, if it is a string
        if type(self.date_string) == type(""):
            month, day, year = map(int, self.date_string.split("/"))
            self.date = datetime.date(year, month, day)

    # def __dict__(self):
    #     return {'type': str(self.ruling),
    #             'date_string': str(self.date_string)
    #             }


