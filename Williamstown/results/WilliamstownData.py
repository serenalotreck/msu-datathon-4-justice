'''
This Library is going to read the text file generated using the http://avepdf.com/ website from the Williamstown pdf files. 

NOTE: It is "working" enough to start gathering statistics.  However, there are still a ton of errors. 

'''

import re # Regulra expresion library

def cleanstring(line, lower=False):
    '''Clean up white space in string with an option to set to lowercase.'''
    line = line.rstrip().lstrip()
    line = re.sub(' +', ' ',line)
    if lower:
        line = line.lower()
    return line

# read file in as a list of lines
def readfile(filename):
    '''Trivially simple command to read in a file as a list of 
    lines while stripping off leading and training spaces'''
    lines = []
    with open(filename) as f:
        lines = f.readlines()

    for ind in range(len(lines)):
        lines[ind] = lines[ind].lstrip().rstrip()
    return lines


def txt2calls(lines):
    '''Spit the lines of a file into seperate calls using Parse cells using call 
    number [19,20]-XXXX as deliminator. The Result is a list of list where each 
    call is a list of lines for the call.'''
    calls = []
    call = []
    for line in lines:
        if line == '':
            pass
        else:
            if re.match("[1-2][9,0]-[0-9]+\s", line[:10]):
                if len(call) > 0:
                    calls.append(call)
                    call = []
            call.append(line)
    if len(call) > 0:
        call.append(line)
    return calls

def parseHeader(line):
    '''Parse the first line of each call. Use error checking to find components.'''
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
    '''Parse the Unit times list into seperate times. Example includes:
    
        Arvd-08:35:49          Clrd-08:36:00
    '''
    unit_str = cleanstring(unit_str, lower=False)
    times = unit_str.split(' ')
    tm_dict = {}
    for tm in times:
        if '-' in tm:
            vals = tm.split('-')
            tm_dict[vals[0].lower()] = vals[-1]
    return tm_dict

def parse_call_list(call, debug=False):
    '''Parse a call list into a dictionary'''
    
    unit_times = ['disp', 'arvd', 'enrt', 'clrd']
    
    if len(call) == 0:
        return
    
    my_call = {}
    
    header = parseHeader(call[0])
    if header: 
        my_call['number'] = header[0]
        my_call['time'] = header[1]
        my_call['reason'] = header[2]
        my_call['action']= header[3]
        
    ind = 0
    individual = ''
    while ind < len(call):
        line = call[ind]
        myline = line.split(':')
        if len(myline) == 2:
            tag = cleanstring(myline[0], lower=True)
            value = cleanstring(myline[1], lower=False)
            if tag[:4] in unit_times:
                print("unit error: "+tag)
            else:
                if tag == 'narrative':
                    if tag in my_call:
                        narrative = my_call['narrative']
                    else:
                        narrative = ''
                    ind +=1
                    while ind < len(call):
                        myline = call[ind].split(':')
                        if len(myline) == 1:
                            narrative += re.sub(' +', ' ',call[ind]) + " "
                        ind += 1
                    my_call['narrative'] = narrative
                else:
                    if tag == "unit":
                        ind += 1;
                        if ind < len(call):
                            unit_info = get_unit_times(call[ind])
                            if 'Units' in my_call:
                                my_call['Units'].append((value, unit_info))
                            else:
                                my_call['Units'] = [(value, unit_info)]
                    else:
                        if tag == "operator" or tag == "owner":
                            individual=tag+"_"
                        my_call[tag] = value
        else:
            if len(myline) > 2:
                if myline[:4] in unit_times:
                    print("unit error: "+tag)
                else:
                    #print(line)
                    tags = re.findall('[\S]+:', line)

                    for tag in reversed(tags):
                        start = line.rindex(tag)
                        value = cleanstring(line[start+len(tag):], lower=True)

                        if len(value) > 0:
                            tag = tag[:-1]
                            my_call[(individual+tag).lower()] = value
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
        my_call = parse_call_list(call)
        call_dicts.append(my_call)
    return call_dicts

def parsefile(filename):
    '''Combine everything into one function call'''
    lines = readfile(filename)
    calls = txt2calls(lines)
    call_dicts = parse_all_calls(calls)
    return [lines, calls, call_dicts]