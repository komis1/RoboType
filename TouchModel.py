### Class to generate a touch model

class TouchModel:

    ## probabilities of substituting a letter for another, based on touch distributions
    subsdict = {}

    def __init__(self, file=False):
        if file:
            self.load_from_file(file)

    ## generate model from tapping simulations
    ## in this case, we simulate tapping every key in the alphabet (passed as a string)
    def generate(self, alphabet, finger, keyboard, times):
        #simulate thousands of taps
        tps = finger.typeSentence(keyboard, alphabet*times)

        #create dict of intended and actual pressed keys
        for i in tps:
            if i['intent'] not in self.subsdict:
                self.subsdict[i['intent']] = {}
            else:
                if i['letter'] not in self.subsdict[i['intent']]:
                    self.subsdict[i['intent']][i['letter']]=0
                else:
                    self.subsdict[i['intent']][i['letter']]+=1

        #create dict of output probabilities for each intended keypress
        for j in self.subsdict:
            sum=0
            for k in self.subsdict[j]:
                sum+=self.subsdict[j][k]
            for k in self.subsdict[j]:
                self.subsdict[j][k] = self.subsdict[j][k]/sum

    ## load pre-generated model from file
    def load_from_file(self, file):
        f=open(file)
        self.subsdict = json.load(f)
        f.close()

    ## save generated model to file
    def save_to_file(self, file):
        f = open(file, 'w')
        f.write(json.dumps(self.subsdict))
        f.close()
