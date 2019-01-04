


# I am fairly certain that section and subsection are irrelevant to the analyzers logic

# cameron - jan 3 2019
# the way i currently have this configured completely discards section and subsection
#todo: find out if section and subsection are relevant

from expungeservice.analyzer.ineligible_crimes_list import IneligibleCrimesList


class Statute(object):
    """ Statute corresponding to a law

    Statutes are represented by numbers in hierarchical manner:
    chapter.subchapter(section)(subsection) e.g. 653.412(5)(c)

    Attributes:
        chapter: An integer that specifies statute chapter.
        subchapter: An integer that specifies statute sub-chapter.
        section: An integer that specifies the section within sub-chapter.
        subsection: A string of length 1 that specifies the sub-section within
                    section.
    """
    def __init__(self, statute_string, chapter=None, subchapter=None, section=None, subsection=None):

        self.statute_string = str(statute_string)
        self.chapter = chapter
        self.subchapter = subchapter
        self.section = section
        self.subsection = subsection
        # TODO we may need to add components beyond subsection

        if len(str(statute_string))>=6: #todo: this is wrong but will kinda work for everything on our list except marijuana crimes.

            statute_string = statute_string.lower() #convert to lowercase

            statute_string = [char for char in statute_string if char not in "abcdefghijklmnopqrstuvwxyz!@#$%^&*() .,;'[]<>?:{}\""] #remove all other chars #todo: fix this it could include weird chars
            statute_string = ''.join(statute_string)

            statute_string = statute_string[0:6] #trim to only first 6

            self.chapter = statute_string[0:3]
            self.subchapter = statute_string[3:7]

            self.statute_string = self.chapter + '.' + self.subchapter

    # def __eq__(self, other):
    #     return (self.chapter == other.chapter and
    #             self.subchapter == other.subchapter and
    #             ((not self.section and not other.section) or
    #              self.section == other.section) and
    #             ((not self.subsection and not other.subsection) or
    #              self.subsection == other.subsection))

    def __str__(self):
         return str(self.statute_string)

    # def __str__(self):
    #     # TODO do these need to have leading zeros?
    #     statute = '{}'.format(self.chapter)
    #     if self.subchapter:
    #         statute = '{}.{:03d}'.format(statute, self.subchapter)
    #     if self.section:
    #         statute = '{}({})'.format(statute, self.section)
    #     if self.subsection:
    #         statute = '{}({})'.format(statute, self.subsection)
    #     return statute



    # Commented this out until we comlplete the parser logic for these

    # def __str__(self):
    #     # TODO do these need to have leading zeros?
    #     statute = '{}'.format(self.chapter)
    #     if self.subchapter:
    #         statute = '{}.{:03d}'.format(statute, self.subchapter)
    #     if self.section:
    #         statute = '{} {}'.format(statute, self.section)
    #     if self.subsection:
    #         statute = '{}({})'.format(statute, self.subsection)
    #     return statute


if __name__ == '__main__':

    #some testing stuff

    list = ['803455',
            '483050',
            '163.175',
            '811175',
            '8111751',
            '806010',
            '8111751',
            '806010',
            '8112101B',
            '163.375',
            '163.427',
            '163.160(2)',
            '163.095',
            '163.095',
            '163.095',
            '166.085',
            '163.427',
            '163.427',
            '161.405(2)(c)',
            '163.095',
            '163.095',
            '163.095',
            '166.085',
            '161.405(2)(a)',
            '163.375',
            '163.427',
            '163.425',
            '163.415',
            '163.415',
            '110151',
            '811110',
            '811100',
            '811100C',
            '43',
            '811.100',
            '43',
            '43',
            '811.100',
            '43',
            '314.075',
            '314.075',
            '314.075']

    for item in list:
        newStatute = Statute(item)
        newStatute.type_elegible_for_expungement()


    exit()

