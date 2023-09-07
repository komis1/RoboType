### Class to build a language model from a text corpus
import xml.etree.ElementTree as ET
import json


class LanguageModel:

    #ngram probabilities stored in this dictionary
    probdict={}

    def __init__(self, keyboard, file=False):
        mytree = ET.parse(keyboard)
        myroot = mytree.getroot()
        for x in myroot.findall('Row'):
            for child in x:
                if 'keyLabel' in child.attrib and len(child.attrib['keyLabel'])==1 and child.attrib['keyLabel'].isalpha():
                    self.probdict[child.attrib['keyLabel']]={}
        #print(self.probdict)
        if not file==False:
            print('lm load from file')
            self.load_from_file(file)

    ## generate the language model from a text file
    def generate(self, file, ngramsize):
        f = open(file)
        lines = f.readlines()
        ngramsize+=1
        count = 0
        for line in lines:
            line=line.strip()
            '''if len(line)>=2:
                for i in range(len(line)-1):
                    if line[i+1] in self.probdict[line[i]]:
                        self.probdict[line[i]][line[i+1]]+=1
                    else:
                        self.probdict[line[i]][line[i+1]]=1'''
            if len(line)>ngramsize:
                #print(line)
                for i in range(len(line)-ngramsize): #walk char per char
                    chunk = line[i:i+ngramsize] #take a chunk of size ngramsize
                    #print('-'+chunk+'-')
                    for k in range(1,ngramsize): #make 1, 2, 3, n-size ngrams
                        ngram = chunk[0:k]
                        target = chunk[k]
                        #print("'"+ngram+"'", "'"+target+"'")
                        if not ngram in self.probdict:
                            self.probdict[ngram] = {}
                        if target in self.probdict[ngram]:
                            self.probdict[ngram][target]+=1
                        else:
                            self.probdict[ngram][target]=1
            count+=1

        #iterate and calc prob for each letter
        for j in self.probdict:
            sum=0
            for k in self.probdict[j]:
                sum+=self.probdict[j][k]
            for k in self.probdict[j]:
                self.probdict[j][k] = self.probdict[j][k]/sum

        f.close()

    ## generate the language model from a pre-loaded corpus (list of strings)
    def generatefromcorpus(self, corpus, ngramsize):
        count = 0
        for line in corpus:
            line=line.strip()
            if len(line)>ngramsize:
                #print(line)
                for i in range(len(line)-ngramsize): #walk char per char
                    chunk = line[i:i+ngramsize] #take a chunk of size ngramsize
                    #print('-'+chunk+'-')
                    for k in range(1,ngramsize): #make 1, 2, 3, n-size ngrams
                        ngram = chunk[0:k]
                        target = chunk[k]
                        #print("'"+ngram+"'", "'"+target+"'")
                        if not ngram in self.probdict:
                            self.probdict[ngram] = {}
                        if target in self.probdict[ngram]:
                            self.probdict[ngram][target]+=1
                        else:
                            self.probdict[ngram][target]=1
            count+=1

        #iterate and calc prob for each letter
        for j in self.probdict:
            sum=0
            for k in self.probdict[j]:
                sum+=self.probdict[j][k]
            for k in self.probdict[j]:
                self.probdict[j][k] = self.probdict[j][k]/sum

    ## load a pre-generated language model from file
    def load_from_file(self, file):
        f=open(file)
        self.probdict = json.load(f)
        f.close()

    ## save generated language model to file
    def save_to_file(self, file):
        f = open(file, 'w')
        f.write(json.dumps(self.probdict))
        f.close()
