from datetime import datetime
import enum

CaseState = enum.Enum('CaseState', 'OPEN CLOSED')

class Case:

    def __init__(self, info, case_number, citation_number, date_location, type_status, charges, case_detail_link, state=None, balance_due=0.0):
        self.name, birth_year = info
        self.birth_year = birth_year
        self.case_number = case_number
        self.citation_number = citation_number[0] if citation_number else ""
        date, self.location = date_location
        self.date = datetime.date(datetime.strptime(date, '%m/%d/%Y'))

        self.violation_type, self.current_status = type_status
        self.charges = charges
        self.case_detail_link = case_detail_link
        self.state = state

        self.balance_due = balance_due

    def setCharges(self, charges): #this function exists to update the charges with more details
        self.charges = charges

    def num_charges(self):
         return len(self.charges)

    def set_state(self, state): #todo: less ambiguous name
        self.state = state



#
# class Case(object):
#     """ Case associated with a Client.
#
#     Attributes:
#
#         #todo: update this list
#
#         charges: A list of Charge(s).
#         state: A CaseState enum.
#         balance_due: A float that tells how much money is owed to the court.
#     """
#     def __init__(self, case_number, citation_number, date, location, violation_type, current_status, charges, case_detail_link, state, balance_due):
#         self.case_number = case_number
#         self.citation_number = citation_number[0] if citation_number else ""
#         self.date = date
#         self.location = location
#
#         self.violation_type = violation_type
#         self.current_status = current_status
#
#         self.charges = charges
#         self.case_detail_link = case_detail_link
#         self.state = state
#         self.balance_due = balance_due


# CaseState = enum.Enum('CaseState', 'OPEN CLOSED')
#
# class Case(object):
#     """ Case associated with a Client.
#
#     Attributes:
#         charges: A list of Charge(s).
#         state: A CaseState enum.
#         balance_due: A float that tells how much money is owed to the court.
#     """
#     def __init__(self, charges, state, balance_due=0.0):
#         self.charges = charges
#         self.state = state
#         self.balance_due = balance_due
#
#     def num_charges(self):
#         return len(self.charges)