import re


def readfile(filename):
    with open(filename, "r") as file:
        lines = file.readlines()
    return lines


def separateCalls(data):
    calls = []
    currentCall = None
    date = None
    for i in range(len(data)):
        if data[i] == "\n" or len(data[i]) < 4:
            continue
        if data[i][:15].find("For    Date") != -1:               # looks for the start of a new date
            date = re.search("[0-1][0-9]/[0-3][0-9]/20[1-2][0,9]", data[i]).group()
        if i == len(data)-1:                                     # if at end of data
            currentCall.text.append(data[i])
            calls.append(currentCall)
            return calls
        elif re.search("^20-", data[i][:4]) is not None or re.search("^.20-", data[i][:4]) is not None:     # if at start of new call
            if currentCall is not None:                       # base case to avoid adding empty call
                calls.append(currentCall)                   # add call to list
            currentCall = Call(date)                        # create new call with date
        if currentCall is not None:                        # add current line to the current call
            currentCall.text.append(data[i])
    return calls


class Call:

    def __init__(self, date):
        self.text = []
        self.date = date
        self.dict = {}

    def reformat(self, string):
        while string[0] == " ":
            string = string[1:]
        while string[-1] == " " or string[-1] == '\n':
            string = string[:-1]
        string = re.sub("\s+", " ", string)
        return string

    def parse_header(self):

        line = self.text[0]
        index_past = 0

        callNumberMatch = re.search("20-\d+", line)
        if callNumberMatch is not None:
            callNumber = callNumberMatch.group()
            index_past = callNumberMatch.span()[1] + 1
        else:
            callNumber = None

        timeMatch = re.search("\d\d\d\d", line[index_past:])
        if timeMatch is not None:
            callTime = timeMatch.group()
            index_past += timeMatch.span()[1] + 1
        else:
            callTime = None

        spaces = 0
        index = len(line) - 1
        while spaces < 8:
            if line[index] == " ":
                spaces += 1
            else:
                spaces = 0
            index -= 1

        callReason = self.reformat(line[index_past:index])
        callAction = self.reformat(line[index + 8:])

        return [callNumber, callTime, callReason, callAction]

    def get_unit_times(self, unit_str):
        times = re.sub(' +', ' ', unit_str).split(' ')
        tm_dict = {}
        for tm in times:
            if '-' in tm:
                vals = tm.split('-')
                tm_dict[vals[0]] = vals[-1]
        return tm_dict

    def parse_call_list(self):
        '''Parse a call list into a dictionary'''

        if self.text is None:
            return

        my_call = {}
        my_call['Call Date'] = self.date

        header = self.parse_header()
        if header:
            my_call['Call Number'] = header[0]
            my_call['Call Time'] = header[1]
            my_call['Call Reason'] = header[2]
            my_call['Call Action'] = header[3]

        ind = 0
        individual = ''
        while ind < len(self.text):
            line = self.text[ind]
            myline = line.split(':')
            if len(myline) == 2:
                tag = myline[0].rstrip().lstrip()
                tag = re.sub(' +', ' ', tag)
                value = myline[1].rstrip().lstrip()
                if tag == 'Narrative':
                    if tag in my_call:
                        narrative = my_call['Narrative']
                    else:
                        narrative = ''
                    ind += 1
                    while ind < len(self.text):
                        myline = self.text[ind].split(':')
                        if len(myline) == 1:
                            narrative += re.sub(' +', ' ', self.text[ind]) + " "
                        ind += 1
                    my_call['Narrative'] = narrative
                else:
                    if tag == "Unit":
                        ind += 1;
                        if ind < len(self.text):
                            unit_info = self.get_unit_times(self.text[ind])
                            if 'Units' in my_call:
                                my_call['Units'].append((value, unit_info))
                            else:
                                my_call['Units'] = [(value, unit_info)]
                    else:
                        if tag == "Operator" or tag == "Owner":
                            individual = tag + "_"
                        my_call[tag] = value
            elif len(myline) > 2:
                tags = re.findall('[\S]+:', line)

                for tag in reversed(tags):
                    start = line.rindex(tag)
                    value = line[start + len(tag):].rstrip().lstrip()

                    if len(value) > 0:
                        tag = tag[:-1]
                        my_call[individual + tag] = value
                        line = line[:line.rindex(tag)]
            ind += 1

        self.dict = my_call
        return (my_call)