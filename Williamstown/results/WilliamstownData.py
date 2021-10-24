import re # Regulra expresion library
import datetime

# wanting to catch things looking like "For Date: mm/dd/yyyy" as these are 
# manually inserted headers to tag the calls based on calendar date.
# They appear once in the pdf file and apply to all calls beneath them 
# until the next "For Date" appears.

# hacky implementation: using a global variable and modifying the output of 
# txt2calls to have tuples as outputs which include the datetimes as well as 
# the original output.
global current_date
current_date = datetime.date(year=1970,month=1,day=1)

# read file in as a list of lines
def readfile(filename):
    lines = []
    with open(filename) as f:
        lines = f.readlines()

    for ind in range(len(lines)):
        lines[ind] = lines[ind].lstrip().rstrip()
    return lines

def fetch_date(line):
    '''
    Checks if a line matches the "For Date" pattern.
    
    Inputs:
        line; a string.
    Returns:
        match: boolean; whether there was a match.
        dt: either a datetime.date object if match is True, else None.
    '''
    import datetime
    
    fordate_pattern = 'For[\ \t]{1,}Date:[\ \t]{1,}([0-9]{2})\/([0-9]{2})\/([0-9]{4}).*'
    fordate_prog = re.compile(fordate_pattern)
    match = fordate_prog.match(line)
    if match is None:
        return (False, match)
    else:
        elements = match.groups()
        dt = datetime.date(
            month=int(elements[0]), 
            day=int(elements[1]), 
            year=int(elements[2])
            )
        return (True, dt)
    #
#

# Parse cells using 20-1 regular expresisons
# Result is a list of list where each call is a list of lines for the call.

def txt2calls(lines):
    global current_date
    calls = []

    call = []
    for line in lines:
        if line == '':
            pass
        # check to see if the date has changed.
        date_questionmark = fetch_date(line)
        if date_questionmark[0]:    # if true, second entry should be datetime
            current_date = date_questionmark[1]
        else:
            if re.match("[1-2][9,0]-[0-9]+\s", line[:10]):
                if len(call) > 0:
                    #calls.append(call)
                    calls.append( (current_date, call) )
                    call = []
            call.append(line)
    if len(call) > 0:
        call.append(line)
    return calls

def parseHeader(line):
    '''Parse the first line of each call. Use error checking to find components.'''
#     print(line)
    index_past = 0
        
    callNumberMatch = re.search("[19,20]-\d+", line)
    if callNumberMatch == None:
        return

    callNumber = callNumberMatch.group()
    index_past = callNumberMatch.span()[1]
    callNumber = line[:index_past]
        
    timeMatch = re.search("\d\d\d\d", line[index_past:])
    if timeMatch is not None:
        callTime = timeMatch.group()
        index_past += timeMatch.span()[1]+1
    else:
        callTime = None
        
    spaces = 0
    index = len(line)-1
    while spaces < 8:
        if index > 0 and index < len(line):
            if line[index] == " ":
                spaces += 1
            else:
                spaces = 0
        else:
            break
        index -= 1
    callReason = re.sub("\s+", " ", line[index_past:index])
    if len(callReason) > 1:
        if callReason[0] == " ":
            callReason = callReason[1:]
        if callReason[-1] == " ":
            callReason = callReason[:-1]
    else:
        callReason=""
    
    callAction = re.sub("\s+", " ", line[index+8:])
    if len(callAction) > 1:
        if callAction[0] == " ":
            callAction = callAction[1:]
        if callAction[-1] == " ":
            callAction = callAction[:-1]
    else:
        callAction=""
        
    return [callNumber, callTime, callReason, callAction]

def get_unit_times(unit_str):
#     print(unit_str)
    times = re.sub(' +', ' ',unit_str).split(' ')
    tm_dict = {}
    for tm in times:
        if '-' in tm:
            vals = tm.split('-')
            tm_dict[vals[0]] = vals[-1]
    return tm_dict

def parse_call_list(call, debug=False):
    '''Parse a call list into a dictionary'''
    
    if len(call) == 0:
        return
    
    my_call = {}
    
    header = parseHeader(call[0])
    if header: 
        my_call['callNumber'] = header[0]
        my_call['callTime'] = header[1]
        my_call['callReason'] = header[2]
        my_call['callAction']= header[3]
#     my_call['header'] = call[0]
    
    ind = 0
    individual = ''
    while ind < len(call):
        line = call[ind]
        myline = line.split(':')
        if len(myline) == 2:
            tag = myline[0].rstrip().lstrip()
            tag = re.sub(' +', ' ',tag)
            value = myline[1].rstrip().lstrip()
            if tag == 'Narrative':
                if tag in my_call:
                    narrative = my_call['Narrative']
                else:
                    narrative = ''
                ind +=1
                while ind < len(call):
                    myline = call[ind].split(':')
                    if len(myline) == 1:
                        narrative += re.sub(' +', ' ',call[ind]) + " "
                    ind += 1
                my_call['Narrative'] = narrative
            else:
                if tag == "Unit":
                    ind += 1;
                    if ind < len(call):
                        unit_info = get_unit_times(call[ind])
                        if 'Units' in my_call:
                            my_call['Units'].append((value, unit_info))
                        else:
                            my_call['Units'] = [(value, unit_info)]
                else:
                    if tag == "Operator" or tag == "Owner":
                        individual=tag+"_"
                    my_call[tag] = value
        else:
            if len(myline) > 2:
                #print(line)
                tags = re.findall('[\S]+:', line)

                for tag in reversed(tags):
                    start = line.rindex(tag)
                    value = line[start+len(tag):].rstrip().lstrip()

                    if len(value) > 0:
                        tag = tag[:-1]
                        my_call[individual+tag] = value
                        line = line[:line.rindex(tag)]

            else:
                if debug:
                    print("Parse Error:  "+line)
                    print("")
        ind +=1

    return(my_call)

def parse_all_calls(calls):
    '''Parse all of the calls'''
    call_dicts =[]
    unit = ''
    for call in calls:
        dt = call[0]    # calendar date of call
        
        my_call = parse_call_list(call[1])
        my_call['date'] = dt # add in datetime to dictionary.
        
        call_dicts.append(my_call)
    return call_dicts


#Combine everything into one call
def parsefile(filename):
    lines = readfile(filename)
    calls = txt2calls(lines)
    call_dicts = parse_all_calls(calls)
    return [lines, calls, call_dicts]