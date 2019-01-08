#!/usr/bin/env python3

import logging

from expungeservice.models.statute import Statute
from expungeservice.models.case import *
from expungeservice.models.charge import *
from expungeservice.expunger.ineligible_crimes_list import *

from operator import attrgetter

from datetime import datetime
from datetime import timedelta


import collections
import enum



#todo: i am not sure if im supposed to be using getters and setters for objects python lets me just set object values however i want but i should probably do that


class ResultCode(enum.Enum):
    INELIGIBLE = 'Ineligible'
    ELIGIBLE = 'Eligible'
    FURTHER_ANALYSIS = 'Further analysis needed'
    EXAMINE = 'Examine'
    NO_ACTION = 'Take no action'
    OPEN_CASE = 'Open Case'

"""
A class for storing individual analysis steps

Attributes:
    result: A boolean that's the result of the check
    check: A string that breifly describes the check
    check_desc: A string that elaborates the check (optional)
"""
CheckResult = collections.namedtuple('CheckResult', 'result check check_desc',
                                     defaults=[None])

class Result(object):
    """
    A class for storing analysis results

    Attributes:
        code: A ResultCode instance.
        statute: A Statute instance that's associated with arrived result.
        date: A datetime.date instance that specifies eligibility date.
        analysis: A list of CheckResult instances that describes the analysis done.
    """
    def __init__(self, code=None, analysis=None,
                 statute=None, date=None):
        self.code = code
        self.analysis = analysis
        self.statute = statute
        self.date = date

    def __str__(self):
        return ' '.join([str(self.code), str(self.analysis), str(self.statute), str(self.date)])

class ResultInElig_137_225_5(Result):

    """
    137.225(5) mandates the following

    class A felony
    sex crime from list A
    traffic crimes

    are not expunged
    """

    def __init__(self, **kwargs):
        Result.__init__(self, code=ResultCode.INELIGIBLE,
                        statute=Statute(137, 225, 5), **kwargs)

class RecordAnalyzer(object):
    """
    A class for analyzing client's records

    Attributes:
        client: A Client instance
    """

    def __init__(self, client):
        self.client = client
        self.analyze()

    # def _is_charge_level(charge, type_, class_):
    #     check = 'Is the charge a {}'.format(type_)
    #     if class_:
    #         check += ' class {}'.format(class_)
    #
    #     result = (charge.level.type_ ==  type_ and
    #               (not class_ or charge.level.class_ == class_))
    #
    #     return CheckResult(check=check, result=result)

    # def _is_charge_statute(charge, statute):
    #     check = 'Does the charge fall under statute: ' + str(statute)
    #     return CheckResult(check=check, result=charge.statute == statute)

    #todo: there is LOTS of duplication between the next three functions and everywhere cameron has been coding
    #todo: maybe instead of searching for equivalent charge objects we should just refer to the original charge object's memory address or whatever that thing is like <expungeservice.models.charge.Charge object at 0x7f1c637d9b38>
    #todo: incorporate the result object from above

    def get_all_charges_sorted_by_date(self):
        chargelist = []

        for case in self.client.cases:
            for charge in case.charges:
                if charge.disposition.type_ == "CONVICTED":
                    chargelist.append(charge)

        sorted_list = sorted(chargelist, key=attrgetter('disposition.date')) # sort list of convictions by date, note: the list is mostly sorted by the parser but not completely sorted so this is in fact necessary
        return sorted_list

    def get_mrc(self):
        return RecordAnalyzer.get_all_charges_sorted_by_date(self)[-1:][0]

    def is_charge_from_last_3_years(self, charge):
        three_years_ago_from_today = datetime.today() - timedelta(days=(365 * 3))  # calculate time delta for twenty years ago

        if charge.disposition.date > three_years_ago_from_today:
            return True

    def get_last_ten_years_of_convictions(self, mrc):

        ten_years_ago_from_today = datetime.today() - timedelta(days=(365 * 10))  # calculate time delta for ten years ago #todo: calculate if this is accurate to within +-1 day
        sorted_list = RecordAnalyzer.get_all_charges_sorted_by_date(self)

        last_ten_years_of_convictions_minus_mrc = []

        for charge in sorted_list:
            if charge != mrc:
                if charge.disposition.date > ten_years_ago_from_today: #todo: is this right?
                    last_ten_years_of_convictions_minus_mrc.append(charge)

        return last_ten_years_of_convictions_minus_mrc


    def is_mrc_time_eligible(self, mrc):

        any_other_convictions_from_last_ten_years = RecordAnalyzer.get_last_ten_years_of_convictions(self, mrc)

        if len(any_other_convictions_from_last_ten_years) > 0:
            ten_years_from_disposition = mrc.disposition.date + timedelta(days=(365 * 10))
            mrc.eligible_when = ten_years_from_disposition
            return Result(ResultCode.INELIGIBLE, "This is MRC. it is Time Eligible beginning at " + str(ten_years_from_disposition), None)
        else:
            if RecordAnalyzer.is_charge_from_last_3_years(self, mrc):
                mrc.time_eligible = True
                mrc.time_eligible_analysis = "This is MRC. it is Time Eligible"
                return True
            else:
                three_years_from_disposition = mrc.disposition.date + timedelta(days=(365 * 3))
                mrc.time_eligible = False
                mrc.time_eligible_analysis = "This is MRC. it is Time Eligible beginning at " + str(three_years_from_disposition)
                mrc.eligible_when = three_years_from_disposition
                return True


    def is_charge_time_eligible(self, charge, mrc):

        # calculate ten years from MRC
        ten_years_from_mrc = mrc.disposition.date + timedelta(days=(365 * 10))  # calculate time delta for twenty years ago #todo: calculate if this is accurate to within +-1 day

        if datetime.today().date() > ten_years_from_mrc:
            logging.info(charge.name + " is time eligible since " + str(ten_years_from_mrc) )
            charge.time_eligible = True
            charge.eligible_when = ten_years_from_mrc
            charge.time_eligible_analysis = "Time eligible since " + str(ten_years_from_mrc)

        if datetime.today().date() < ten_years_from_mrc:
            logging.info(charge.name + " is not time eligible unitl " + str(ten_years_from_mrc))
            charge.time_eligible = True
            charge.eligible_when = ten_years_from_mrc
            charge.time_eligible_analysis = "Ineligible under 137.225(7)(b). Time Eligiblity begins " + str(ten_years_from_mrc)

    def set_all_other_charges_to_ineligible_until(self, mrc):

        #todo: maybe rewrite this to say more intelligent things like, time eligible since....

        for case in self.client.cases:
            for charge in case.charges:
                if charge != mrc:
                    RecordAnalyzer.is_charge_time_eligible(self, charge, mrc) #this function sets the appropriate properties automatically

    def does_record_contain_conviction_from_last_ten_years(self):

        for case in self.client.cases:
            for charge in case.charges:
                if charge.disposition.type_ == "CONVICTED":

                    ten_years_ago = datetime.today() - timedelta(days=(365*10)) #calculate time delta for twenty years ago #todo: calculate if this is accurate to within +-1 day

                    if ten_years_ago.date() < charge.disposition.date:
                        return True

        return False

    def _have_open_case(self):
        check = 'Is there a open case for the client'
        result = any([case.state == CaseState.OPEN for case in self.client.cases])
        return CheckResult(check=check, result=result)

    """
    Run Time Eligibility analysis on the client and their records

    TODO: make it return analysis for each charge as well (which is supposed
    to be an update on eligibility date and relevan statutes)

    Returns:
        An Result instance
    """
    def time_eligibility(self):
        analysis = []

        #check for any Open Cases
        analysis.append(self._have_open_case())
        if analysis[-1].result:
            return Result(ResultCode.OPEN_CASE, analysis)

        #check for any charges in last ten years
        if RecordAnalyzer.does_record_contain_conviction_from_last_ten_years(self):
            return False

        mrc = RecordAnalyzer.get_mrc(self)

        self.set_all_other_charges_to_ineligible_until(mrc)

        return Result(ResultCode.NO_ACTION)

    """
    Analyze which records are expungeable

    The method sets the Charge instance's result attribute with type eligibility
    analysis result.

    Returns:
        A tuple consisting of:
            - A Result instance that describes the Time Eligibility analysis.
    """

    def analyze(self): #todo: conform to the comment above

        #this checks time eligibility for all charges on all cases
        self.time_eligibility()

        #this checks TYPE eligibility for all charges

        for case in self.client.cases: #iterate through all cases and charges to check type eligibility
            for charge in case.charges:

                # #todo: move this to its own function since it is basically the
                #           type eligibilty function and time eligibility has its own function

                if charge.statute.chapter == None: #todo: throw errror
                    logging.warning(charge.name)
                    logging.warning("error")

                charge.type_eligible = self.type_eligibility(charge)

                if charge.type_eligible.code == ResultCode.INELIGIBLE:
                    charge.eligible_when = "never" #logging.info("failed Type Eligibility tree: " + charge.name + " " + result.analysis)


                #if charge has passed type and time eligibility checks
                if charge.type_eligible.code == ResultCode.ELIGIBLE and charge.time_eligible.code == ResultCode.ELIGIBLE:
                    charge.eligible_now = True
                else:
                    charge.eligible_now = False


    """
    these are helper functions for type eligiblilty
    """
    def is_crime_list_B(charge):

        for item in CrimesListB:
            if item == charge.statute:
                return True

        return False

    def is_crime_list_A(charge):
        try:
            for item in CrimesListA:

                if len(item) == 2 and isinstance(item, list):  # if this is a range of values

                    lower_chapter = int(item[0][0:3])
                    lower_subchapter = int(item[0][4:7])

                    upper_chapter = int(item[1][0:3])
                    upper_subchapter = int(item[1][4:7])

                    if int(charge.statute.chapter) <= upper_chapter and int(charge.statute.chapter) >= lower_chapter:
                        if int(charge.statute.subchapter) <= upper_subchapter and int(charge.statute.subchapter) >= lower_subchapter:

                            logging.info(charge.statute.__str__() + " is on list A")
                            return True  # return false and the reason why its false
            return False

        except:
            logging.warning("Error searching list A for statute: " + str(charge.statute.chapter) + "." + str(charge.statute.subchapter))


    def is_crime_driving_crime(charge):

        for item in DrivingCrimes:
            if len(item) == 2 and isinstance(object, (list,)):  # if this is a range of values

                lower_chapter = item[0][0:3]
                lower_subchapter = item[0][4:7]

                upper_chapter = item[1][0:3]
                upper_subchapter = item[1][4:7]

                if charge.statute.chapter <= upper_chapter and charge.statute.chapter >= lower_chapter:
                    if charge.statute.subchapter <= upper_subchapter and charge.statute.subchapter >= lower_subchapter:

                        #print(charge.statute.__str__() + " is NOT on list A")
                        return True  # return false and the reason why its false
        return False

    def is_crime_marijuana_list(charge):    #todo: this function needs repair
        for item in MarijuanaIneligible:
            if item == charge.statute:
                return True
        return False

    def is_charge_PCS_schedule_1(charge):
        if charge.name == "PCS":            #todo: this is broken, find how to identify this charge
            return True

    def is_charge_traffic_violation(charge):

        if charge.statute.chapter == None:   #todo: throw error
            return False

        if int(charge.statute.chapter) <= 900 and int(charge.statute.chapter) >= 800:
            return True
        return False

    def is_charge_level_violation( charge):
        if charge.level.type_ == "VIOLATION":
            return True
        return False

    def is_charge_misdemeanor( charge):
        if charge.level.type_ == "MISDEMEANOR":
            return True
        return False

    def is_charge_felony_class_C( charge):
        if charge.level.type_ == "FELONY" and charge.level.class_ == "C":
            return True
        return False

    def is_charge_felony_class_B(charge):
        if charge.level.type_ == "FELONY" and charge.level.class_ == "B":
            return True
        return False

    def is_charge_felony_class_A(charge):
        if charge.level.type_ == "FELONY" and charge.level.class_ == "A":
            return True
        return False

    def does_record_contain_arrest_or_conviction_in_last_20_years(client):
        for case in client.cases:
            for charge in case.charges:
                if charge.disposition.type_ == "CONVICTED":
                    twenty_years_ago_date = datetime.today() - timedelta(days=(365*20)) #calculate time delta for twenty years ago #todo: calculate if this is accurate to within +-1 days
                    if twenty_years_ago_date.date() < charge.disposition.date:
                        return True

        return False

    def is_charge_more_than_1_year_old(self, charge):
        one_year_ago_date = datetime.today() - timedelta(days=(365)) #calculate time delta for one year ago #todo: calculate if this is accurate to within +-1 days

        if one_year_ago_date.date() < charge.disposition.date:
            return True #todo: combine all these to return a == b
        return False

    def is_charge_dismissal_or_aquittal(charge):
        if charge.disposition.type_== "DISMISSED" or charge.disposition.type_== "AQUITTED": #todo: i dont know if "AQUITTED" is a valid type
            return True
        return False

    def is_charge_no_complaint(charge):
        if charge.disposition.type_== "NO COMPLAINT": #todo: not sure if "NO COMPLAINT" is a valid type or if its even in this object
            return True
        return False

    """
        Run Type Eligibility analysis on a charge

        Args:
            charge: A Charge instance

        Returns:
            A Result instance
        """

    def type_eligibility(self, charge):
        analysis = ""
        #
        # analysis.append(RecordAnalyzer.is_charge_felony_class_A(charge, 'FELONY', 'A'))
        # if analysis[-1].result:
        #     return ResultInElig_137_225_5(analysis=analysis)

        # analysis.append(RecordAnalyzer._is_charge_sex_crime(charge))
        # if analysis[-1].result:
        #     return ResultInElig_137_225_5(analysis=analysis)
        #
        # analysis.append(RecordAnalyzer._is_charge_traffic_crime(charge))
        # if analysis[-1].result:
        #     return ResultInElig_137_225_5(analysis=analysis)

        # analysis.append(RecordAnalyzer.is)

        #todo: add the commented logging.info things to the result object for back tracing purposes


        #type eligibility tree

        if RecordAnalyzer.is_charge_felony_class_A(charge):
            #logging.info('felony class A')
            return Result(ResultCode.INELIGIBLE, "Ineligible", "137.225(5)")

        if RecordAnalyzer.is_crime_list_A(charge) == True:
            #logging.info('crime list A')
            return Result(ResultCode.INELIGIBLE, "Ineligible", "137.225(5)")

        if RecordAnalyzer.is_crime_driving_crime(charge) == True:
            #logging.info('crime list Driving')
            return Result(ResultCode.INELIGIBLE, "Ineligible", "137.225(5)")

        if RecordAnalyzer.is_crime_list_B(charge) == True:
            #logging.info('crime list b')
            return Result(ResultCode.ELIGIBLE, "Further Analysis Needed", "")

        if RecordAnalyzer.is_crime_marijuana_list(charge) == True:  #todo: this  one is broken and will never be true
            #logging.info('crime list marijuana')
            return Result(ResultCode.INELIGIBLE, "Marijuana Ineligible", "") #todo: find out waht this is

        #positive eligibilty tree

        if RecordAnalyzer.is_charge_PCS_schedule_1(charge) == True:
            #logging.info('pcs 1')
            return Result(ResultCode.ELIGIBLE, "Eligible", "137.225(5)")

        if RecordAnalyzer.is_charge_traffic_violation(charge) == True:
            #logging.info('traffic violation')
            return Result(ResultCode.INELIGIBLE, "Ineligible", "137.225(5)")

        if RecordAnalyzer.is_charge_level_violation(charge) == True:
            #logging.info('non traffic crime at level: violation')
            return Result(ResultCode.ELIGIBLE, "Eligible", "137.225(5)(d)")

        elif RecordAnalyzer.is_charge_misdemeanor(charge) == True:
            #logging.info('misdemeanor')
            return Result(ResultCode.ELIGIBLE, "Eligible", "137.225(5)(b)")

        elif RecordAnalyzer.is_charge_felony_class_C(charge) == True:
            #logging.info('felony class c')
            return Result(ResultCode.ELIGIBLE, "Eligible", "137.225(5)(b)")

        elif RecordAnalyzer.is_charge_felony_class_B(charge) == True:
            if RecordAnalyzer.does_record_contain_arrest_or_conviction_in_last_20_years(self.client): #todo: this operation's results could maybe be pre computed and stored somewhere since this is kinda expensive, but maybe ill leave it since it rarely gets called.
                #logging.info('felony class B + conviction within 20 yrs')
                return Result(ResultCode.INELIGIBLE, "Ineligible", "137.225(5)(a)(A)(i)")
            else:
                #logging.info('felony class B + NO conviction within 20 yrs')
                return Result(ResultCode.ELIGIBLE, "Further Analysis Needed", None)

        elif RecordAnalyzer.is_charge_dismissal_or_aquittal(charge) == True:
            #logging.info('aquitted or dismissed')
            return Result(ResultCode.ELIGIBLE, "Eligible", "137.225(5)(b)")

        elif RecordAnalyzer.is_charge_no_complaint(charge) == True: #todo: no complaint is not behaving properly
            if RecordAnalyzer.is_charge_more_than_1_year_old(charge) == True:
                #logging.info('charge is no_complaint + older than 1 year')
                return Result(ResultCode.ELIGIBLE, "Eligible", "137.225(5)(b)")

        elif RecordAnalyzer.is_charge_no_complaint(charge) == False:
            #logging.info('no complaint')
            return Result(ResultCode.ELIGIBLE, "Further Analysis Needed", None)
        else:
            logging.info("this has somehow escaped the flow chart") #todo should this should throw an error?



