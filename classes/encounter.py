import datetime as dt
class Encounter():
    def __init__(self, patientid, date, type):
        self.date = date
        if type(date) is not dt.datetime:
            self.date = dt.datetime(date)
        self.type = type
        self.patientid

    def __lt__(self, other):
        return self.date < other.date
