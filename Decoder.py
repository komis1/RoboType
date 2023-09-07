### Class to simulate function of a statistical decoder

### Work in progress!!!

class Decoder:

    def __init__(self, klayoutfile, lmfile, tmodelfile, ngramsize):
        self.langmodel = LanguageModel(klayoutfile, file=lmfile)
        self.tmodel = TouchModel(tmodelfile)
        self.ngramsize = ngramsize
        print('hello decoder')

    def decode(self, buffer, currlett):
        #print('start decode')
        print ('hit', currlett)
        buffer = "".join(buffer)
        #probabilities of wanting to press other keys instead of currlett based on touch model
        if currlett in self.tmodel.subsdict:
            touchprobs = self.tmodel.subsdict[currlett]
        else:
            touchprobs = {}

        #probabilities of next keys from current buffer, based on lang model
        if buffer in self.langmodel.probdict:# and currlett in self.langmodel.probdict[buffer]:
            langprobs = self.langmodel.probdict[buffer]
        else:
            langprobs = {}

        #go through all probs and create unified dict
        uniprobs={}
        for p in touchprobs:
            if p not in uniprobs:
                uniprobs[p]={"tp":touchprobs[p]}
            else:
                uniprobs[p]['tp']=touchprobs[p]
        for p in langprobs:
            if p not in uniprobs:
                uniprobs[p]={"lp":langprobs[p]}
            else:
                uniprobs[p]['lp']=langprobs[p]
        #go through unidict and create final prob
        #final prob = prob of pressing possible keys * prob of keypress following previous ones

        #print(uniprobs)

        outletter = currlett

        max = 0
        finalprob=0
        for p in uniprobs:
            if 'tp' in uniprobs[p]:
                if 'lp' in uniprobs[p]: #probs from both
                    finalprob= 0.3*uniprobs[p]['tp']+0.7*uniprobs[p]['lp']
                else:
                    finalprob = 0.3*uniprobs[p]['tp']*+0.7*0.0001
            else:
                if 'lp' in uniprobs[p]:
                    finalprob = 0.7*uniprobs[p]['lp']+0.3*0.0001
                else:
                    finalprob = 0
            #print(p,finalprob)
            if finalprob>max:
                max=finalprob
                outletter=p




        #
        #for i in probs:
        #    if len(i)==1:
        #        if i!=' ':
                    #final prob = prob of pressing possible keys * prob of keypress following previous ones
                    #based on language model
        #            if i in self.langmodel.probdict[buffer]:
        #                probs[i]=probs[i]*self.langmodel.probdict[buffer][i]
        #            else:
        #                probs[i]=0

                    #find key with greatest final prob
        #            if probs[i]>max:
        #                max = probs[i]
        #                outletter = i

        if outletter!=currlett:
            print('changed '+currlett+' to '+outletter+' after buff:'+buffer)
        #else:
        #    print('no change')

        return(outletter)
