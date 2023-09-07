#!/usr/bin/env python
# coding: utf-8

# In[2]:

import datetime

from Decoder import *
from Finger import *
from LanguageModel import *
from TouchModel import *
from Keyboard import *
from metrics import *
from read_corpus import *
from visualiser import *



### Demonstration of RoboType ###

## create a language model

lm = LanguageModel('keyboards/qwerty.xml')
# from a phrase set
#lm.generatefromcorpus(read_leiva('phrase_sets/leiva_and_sanchis-trilles/en-sel2k.tok.lc'),4)
# from a text file (in this case, a list of english words)
lm.generate('support_files/words_alpha.txt',3)
lm.save_to_file("languagemodel.json")
# test it (what follows 'ind'?)
print('ngram = ind', lm.probdict['ind'])
print('ngram = in', lm.probdict['in'])


## create a touch Model
#tm = TouchModel()
#alphabet = "abcdefghijklmnopqrstuvwxyz"
#tm.generate(alphabet, myfinger, mykeyboard, 2000)
#tm.save_to_file('touchmodel.json')

## create a keyboard without statistical decoder

mykeyboard = Keyboard('keyboards/qwerty.xml', 'languagemodel.json', 'touchmodel.json', [1400,1000],[0,0], usedecoder=False)
mykeyboard.plot(10,7)

## create a virtual experiment involving all synthetic participants

f=open('virtual_participants/popts_all.json')
participants = sorted(list(json.load(f).keys()))
f.close()

# load a phrase set
corpus = read_enron('phrase_sets/vertanen_and_kristensson')

start_time = datetime.datetime.now()

#input stream will be stored here
tpsall = []

#for each participant
for p in participants:

    phraseset=[]
    #participant's text entry stats
    wpms=[]
    kspcs=[]

    #get 50 random phrases from phrase set
    indexes = random.sample(range(0, 200), 50)
    for i in indexes:
        phraseset.append(corpus[i])

    #create participant finger
    myfinger=Finger('virtual_participants/popts_all.json', int(p))

    #set visual search time for participant
    myfinger.vst=50 #milliseconds
    myfinger.vst_stdev_factor=0.2
    #participant input stream for each phrase
    tps1=[]

    #for each phrase, do the actual typing (with correction)
    for line in phraseset:
        #type the phrase
        tps1=(myfinger.typeSentenceWithCorrection(mykeyboard, line, 1))
        #add phrase text entry metrics to participant stats
        wpms.append(wpm(tps1))
        kspcs.append(kspc(tps1, line))
        #add phrase input stream to overall set
        tpsall.extend(tps1)

    #print participant stats
    print(int(p), np.mean(wpms), np.mean(kspcs))

#calculate experiment duration
end_time = datetime.datetime.now()
print(end_time - start_time)

#visualise experiment outcomes
plotTaps(tpsall,mykeyboard, 10,7)
