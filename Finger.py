### Class to simulate finger kinematics
import json
import numpy as np
import math
import random
from metrics import *

class Finger:

    target_matches = 0
    target_misses = 0

    #speed profiles approximate a lognormal pattern https://www.frontiersin.org/articles/10.3389/fpsyg.2013.00945/full
    #visual scan time - novice users hover finger over keyboard while searching for new target https://www.yorku.ca/mack/bit4.html
    #experts take approx 450ms ± 50ms average to search for next key https://dl.acm.org/doi/pdf/10.1145/3025453.3025580

    def __init__(self,paramfile,userid):
        self.position=[0,0]
        f=open('support_files/slides.json')
        self.slideavgs = json.load(f)
        f.close()
        f=open(paramfile)
        params = json.load(f)
        self.logfuncparams = params[str(userid)]['logfunc_params']
        self.stdevmap = params[str(userid)]['stdev_map']
        self.vst  = 10 #params[str(userid)]['visual_scan_time']
        self.vst_sd = 0.2 #params[str(userid)]['visual_scan_time_sd_factor']
        self.motor_system_stdev_factor = params[str(userid)]['motor_system_stdev_factor']
        self.max_speed = params[str(userid)]['max_speed']
        f.close()

    def calcTime(self, start, end, endwidth):
        A = math.sqrt((start[0]-end[0])**2+(start[1]-end[1])**2)
        s = endwidth/self.motor_system_stdev_factor
        sa = endwidth/(self.speed/1500) #hacky hacky way

        #ffits
        time = a+b*log2(A/math.sqrt(2*math.pi*math.e*(s**2-sa**2))+1)

    ## calculates finger movement speed as a function of the distance it has to travel
    def logfunc2(self, dist, a, b, c):

        rng = np.random.default_rng()
        predval = a*np.log(b+dist)+c
        keylist = list(self.stdevmap.keys())
        idx = 0
        for i in range(len(keylist)):
            if dist<float(keylist[i]):
                break
            else:
                idx=i
        #mu, sigma, samples
        return abs(rng.normal(predval, self.stdevmap[keylist[idx]],1)[0])

    ## find space key nearest to finger position (when keyboard has multiple spc keys)
    def findNearestSpace(self, keyboard):
        return [n.object for n in keyboard.spaceidx.nearest(
            (self.position[0],self.position[1],self.position[0],self.position[1]),
            objects=True)][0]

    ### creates a tap on the screen targeting a specific letter,
    ### returns which letter was actually pressed
    def moveFingerKinematic(self, target, keyboard, speed_factor, slides='on'):
        #finger lands with 2 distributions: 1) inherent imprecision of motor system and 2) based on user speed
        #resulting in ffits law 10.1145/2470654.2466180

        #fingers will slide in the direction of movement 10.1145/3472749.3474816
        #fingers tend to hit off-center from the target 10.1145/2371574.2371612

        if target==' ':
            target=self.findNearestSpace(keyboard)
            #print('new target', target)

        targetletter = keyboard.keylist[target]['letter']

        #self.speed = speed
        rng = np.random.default_rng()
        outcome = {}

        targetx = keyboard.keylist[target]['center'][0]
        targety = round(keyboard.keylist[target]['center'][1]+keyboard.keylist[target]['ylen']*0.2)

        #jitter based on motor system
        xrange = round(keyboard.keylist[target]['xlen']*self.motor_system_stdev_factor)
        yrange = round((keyboard.keylist[target]['ylen']/4)*self.motor_system_stdev_factor)

        xjitter = round(rng.normal(0, xrange, 1)[0]) #mean = 0, sigma = xrange (keylen/factor)
        yjitter = round(rng.normal(0, yrange, 1)[0])

        motionlength = math.sqrt(pow((targety-self.position[1]),2) + pow((targetx-self.position[0]),2))
        if motionlength==0:
            motionlength=1 #move 1px min

        chosenspeed = self.logfunc2(motionlength, self.logfuncparams['a'],self.logfuncparams['b'],self.logfuncparams['c'])
        chosenspeed = chosenspeed * speed_factor # whether in more of a hurry (e.g. 1.2) or not (e.g 0.8)

        try:
            #logfunc can return negatives for small dist values, use abs
            sxrange = abs(round(keyboard.keylist[target]['xlen']*(chosenspeed/self.max_speed))) #user 114 max hspeed = 6.71px/ms
            syrange = abs(round(keyboard.keylist[target]['ylen']*(chosenspeed/self.max_speed)))
            sxjitter = round(rng.normal(0, sxrange, 1)[0]) #mean = 0, sigma = xrange (keylen/factor)
            syjitter = round(rng.normal(0, syrange, 1)[0])
        except Exception as e:
            print(e)
            print(target, chosenspeed, keyboard.keylist[target]['xlen'] )
            print(motionlength, self.logfuncparams['a'],self.logfuncparams['b'],self.logfuncparams['c'])
            print(motionlength, chosenspeed, sxrange)


        #calculate touch down coordinates
        targetx+=xjitter+sxjitter
        targety+=yjitter+syjitter

        #limit touch down to physical bounds (left, right, bottom)
        if targetx<0:
            targetx=0
        if targetx>keyboard.xdim:
            targetx=keyboard.xdim
        if targety>keyboard.ydim:
            targety=keyboard.ydim

        if slides=='on':
            #random percentage slide of motionlength, capped at 14 pixels
            slidepct = rng.chisquare(np.mean(self.slideavgs[targetletter]),1)[0]
            if slidepct>14:
                slidepct=14

            costheta = (targetx-self.position[0])/motionlength
            sintheta = (targety-self.position[1])/motionlength

            slidex = round(targetx + slidepct*costheta)
            slidey = round(targety + slidepct*sintheta)

            #limit touch slides to physical bounds (left, right, bottom)
            if slidex<0:
                slidex=0
            if slidex>keyboard.xdim:
                slidex=keyboard.xdim
            if slidey>keyboard.ydim:
                slidey=keyboard.ydim


            self.position=[slidex, slidey]
        
        else:
            self.position=[targetx, targety]

        outcome['letter']=keyboard.outputLetter(self.position)
        outcome['intent']=targetletter
        outcome['tap']={'x':self.position[0],'y':self.position[1]}
        outcome['touchdown']={'x':targetx,'y':targety}
        outcome['touchup']={'x':self.position[0],'y':self.position[1]}
        outcome['speed']=chosenspeed
        outcome['vst']=abs(rng.normal(self.vst, self.vst*self.vst_sd, 1)[0])
        outcome['time']=motionlength/chosenspeed + outcome['vst']
        outcome['motionlength']=motionlength

        if outcome['letter'] == target:
            self.target_matches+=1
        else:
            self.target_misses+=1

        return outcome

    ## type a sentence without attempting to correct errors
    def typeSentence(self, keyboard, sentence, speed):
        #reset to keyboard center at start
        self.position=[round(keyboard.xdim/2),round(keyboard.ydim/2) ]
        #reset keyboard buffer
        keyboard.outputbuffer =[]
        dist = 0
        taps = []
        intended = []
        for i in range(len(sentence)):
            output = self.moveFingerKinematic(sentence[i], keyboard, speed)
            taps.append(output)
        return taps

    ## type a key and attempt to correct errors, if they occur
    def typeKeyWithCorrection(self, keyboard, target, speed, noticeprob, slides):
        #orig_notice_prob=noticeprob
        attempts=[]
        hit = False
        while(hit==False):
            #try to hit the key
            attempt = self.moveFingerKinematic(target, keyboard, speed)
            attempts.append(attempt)
            
            #if error made
            if attempt['letter']!=attempt['intent']:
                
                #calculate probability of noticing the error
                rng = np.random.default_rng()
                prob=rng.random()
                
                
                #if noticed, proceed to correct
                if prob<noticeprob:
                    #print("noticed! np=",noticeprob," prob=", prob, "pressed", attempt['letter']," wanted ",attempt['intent'])
                    #check that it wasn't a non-functional key (shift, none), and try to delete it
                    #special case is if you want to press a letter (eg l,m,p) and instead hit delete
                        #in this case we have to repeat the previous input
                    if attempt['letter'] not in ['none','shift', '123', 'return', 'done', 'delete','language']:
                        delpressed = False
                        while (delpressed == False):
                            if keyboard.usedecoder:
                                keyboard.usedecoder=False #deactivate decoder otherwise we will be forever stuck
                                keyboard.decoderdisabled=True
                            delattempt = self.moveFingerKinematic('delete', keyboard, speed, slides=slides)
                            attempts.append(delattempt)
                            if delattempt['letter']!=delattempt['intent']: #didn't hit del successfully
                                #now be super careful since we know we already made a mistake before
                                moreattempts = self.typeKeyWithCorrection(keyboard, 'delete', speed, noticeprob=1.0, slides=slides)
                            else:
                                delpressed = True
                                if len(keyboard.outputbuffer)!=0:
                                    keyboard.outputbuffer.pop()
                                if keyboard.decoderdisabled:
                                    decoderdisabled=False
                                    keyboard.usedecoder=True
                    else: #it was a non-func, non-del key, try to press it again
                        hit=False
                        #now be super careful since we know we already made a mistake before
                        noticeprob=1.0
                else: #not noticed
                    #print("unnoticed! np=",noticeprob," prob=", prob, "pressed", attempt['letter']," wanted ",attempt['intent'])
                    hit=True
                    if attempt['letter'] not in ['none','shift', '123', 'return', 'done', 'delete','language']:
                        keyboard.outputbuffer.append(attempt['letter'])
            else:
                hit=True
                keyboard.outputbuffer.append(attempt['letter'])
                
        return attempts

    ## type a sentence and attempt to correct errors, if they occur
    def typeSentenceWithCorrection(self, keyboard, sentence, speed, noticeprob, slides='on'):
        #reset to keyboard center at start
        self.position=[round(keyboard.xdim/2),round(keyboard.ydim/2) ]
        #reset keyboard buffer
        keyboard.outputbuffer = []
        dist = 0
        taps = []
        intended = []
        for i in range(len(sentence)):
            taps.extend(self.typeKeyWithCorrection(keyboard,sentence[i],speed, noticeprob, slides))
            
        return {"sentence": sentence,
                "output": "".join(keyboard.outputbuffer), 
                "wpm": wpm(taps),
                "kspc": kspc(taps, sentence),
                "taps": taps}
