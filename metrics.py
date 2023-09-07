### Utility functions to calculate text entry metrics from produced input stream dictionaries

def wpm(taps):
    #exclude shift, bsp etc
    typed_entries = 0
    time = 0
    for i in range(len(taps)):
        if len(taps[i]['letter'])==1: # and taps[i]['letter'].isalpha():
            typed_entries+=1
        time+=taps[i]['time']
    minutes=(time/1000/60)
    return (typed_entries/5)/minutes

def kspc(taps, line):
    #exclude shift, bsp etc
    typed_entries = 0
    for i in range(len(taps)):
        if len(taps[i]['letter'])==1:
            typed_entries+=1
    return typed_entries/len(line)
