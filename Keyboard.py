### Class to simulate virtual keyboards
import xml.etree.ElementTree as ET
from rtree import index
import math
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import re

class Keyboard:

    keylist = {}
    keywidth = 0
    usedecoder = False
    decoderdisabled = False
    decoderbuffer = []
    
    xdim=0
    ydim=0
    maxdist=0
    xdim_phys=0
    ydim_phys=0
    outputbuffer = []
    current_word = []
  
    

    def __init__(self, kfile, lmfile, tmfile, dims_px, dims_mm, usedecoder=False, decoderngrams=4):
        self.xdim=dims_px[0]
        self.ydim=dims_px[1]
        self.xdim_phys=dims_mm[0]
        self.ydim_phys=dims_mm[1]

        self.readxml(kfile, self.xdim, self.ydim)

        self.usedecoder = usedecoder
        if self.usedecoder:
            self.decoder = Decoder(kfile, lmfile, tmfile, decoderngrams)
            self.decoderngrams = decoderngrams
            self.decoderdisabled = False

        dists = []
        keys = list(self.keylist.keys())
        for i in range (len(keys)-1):
            for j in range (i+1,len(keys)-1):
                dist = math.sqrt((self.keylist[keys[j]]['center'][0]-self.keylist[keys[i]]['center'][0])**2 + (self.keylist[keys[j]]['center'][1]-self.keylist[keys[i]]['center'][1])**2)
                dists.append(dist)
        self.maxdist=max(dists)
        print(self.maxdist)
        print(self.usedecoder)


    ## print keyboard letters and dimensions
    def printkeyboard(self):
        print("keyboard size "+str(self.xdim)+" x "+str(self.ydim))
        for i in self.keylist:
            print(i)
            print()
        print(self.keylist)

    ### matches xy finger coordinates, with key bounding boxes, and returns the key
    ### optionally uses a decoder to correct the pressed key
    def outputLetter(self, fingerpos):
        letters = list(
                self.idx.intersection(
                    (fingerpos[0], fingerpos[1], fingerpos[0], fingerpos[1]),objects='raw')
                )
        if len(letters)==1: #we hit a key
            if self.usedecoder and len(letters[0])==1: #predict likely key except special ones
                #if len(self.decoderbuffer)==self.decoderngrams:
                if len(self.decoderbuffer)>0: #don't decode if first letter
                    letters[0] = self.decoder.decode(self.decoderbuffer, letters[0])

                #add to buffer
                if len(self.decoderbuffer)>=self.decoderngrams-1: #Remove earliest if full
                    self.decoderbuffer.pop(0)
                if len(letters[0])==1: #don't put in deletes, nones etc
                    self.decoderbuffer.append(letters[0])

                #if letters[0]==' ': #clear the buffer on space
                #    self.decoderbuffer=[]
                
            #if len(letters[0])==1: #not a special key
            #    self.current_word.append[letters[0]]
            #    if re.search("[\s\p{P}]"g,letters[0]): 
            #        #is a space or word terminator, commit the word
            #        self.current_word=[]
            #        self.outputbuffer+=self.current_word
                    
            return(letters[0])
        else:
            return('none')

    ## create a keyboard from an XML file
    def readxml(self,file, xdim, ydim):
        self.keylist={}
        mytree = ET.parse(file)
        myroot = mytree.getroot()

        kw = round(float(myroot.attrib['keyWidth'].split("%")[0])*xdim/100)
        kh = round(float(myroot.attrib['keyHeight'].split("%")[0]))*ydim/100

        hkeygap = round(float(myroot.attrib['horizontalGap'].split("%")[0])*xdim/100)
        vkeygap = round(float(myroot.attrib['verticalGap'].split("%")[0])*ydim/100)

        actualkh = kh-vkeygap

        self.keywidth=kw

        print("standard key dims", kw, kh)

        rowcount = -1
        keycount = -1
        for x in myroot.findall('Row'):
            rowcount+=1
            extragap = 0
            prevcenter = [0,0]
            prevlen=0

            for child in x:

                keycount+=1
                klabel = ''
                center=[0,0]
                actualw = 0

                if 'keyWidth' in child.attrib: #special key
                    actualw=round(float(child.attrib['keyWidth'].split("%")[0])*xdim/100)
                else:
                    actualw=kw

                actualw = actualw-hkeygap

                if 'horizontalGap' in child.attrib:
                    extragap=round(float(child.attrib['horizontalGap'].split("%")[0])*xdim/100)

                if keycount==0:
                    center[0] = extragap+hkeygap/2+actualw/2
                else:
                    center[0] = prevcenter[0]+prevlen/2+actualw/2+hkeygap

                center[1]= kh/2+rowcount*kh



                if 'keyLabel' in child.attrib:
                    klabel=child.attrib['keyLabel']
                else:
                    klabel=child.attrib['keyIcon'].split("_")[2]

                kletter = klabel

                if all(c in ('_') for c in klabel): #is an additional spacebar
                    kletter = ' '

                key ={
                    'letter': kletter,
                    'center':center,
                    'xlen':actualw,
                    'ylen':actualkh,
                    #left bottom right top
                    'bbox':{
                            'left':center[0]-actualw/2,
                            'bottom':center[1]-actualkh/2,
                            'right':center[0]+actualw/2,
                            'top':center[1]+actualkh/2
                            }
                    }
                #print(klabel, center, key['bbox'], actualw, kh)
                self.keylist[klabel]=key
                prevcenter = center
                prevlen = actualw

            keycount=-1

        #rtree index
        self.idx = index.Index()
        self.spaceidx = index.Index()

        counter=0
        for i in self.keylist:
            #insert in master rtree
            self.idx.insert(counter, (self.keylist[i]['bbox']['left'],
                                              self.keylist[i]['bbox']['bottom'],
                                              self.keylist[i]['bbox']['right'],
                                              self.keylist[i]['bbox']['top']), self.keylist[i]['letter'])

            if all(c in ('_') for c in i) or i==' ': #is a space key
                self.spaceidx.insert(counter, (self.keylist[i]['bbox']['left'],
                                              self.keylist[i]['bbox']['bottom'],
                                              self.keylist[i]['bbox']['right'],
                                              self.keylist[i]['bbox']['top']), i)
            counter+=1

    ## visualise the keyboard
    def plot(self,figlen,figw):
        fig, ax = plt.subplots(figsize=(figlen, figw))

        rect = Rectangle((0,-self.ydim), self.xdim,self.ydim,
                             linewidth=1,edgecolor='black',facecolor='darkgrey')
        ax.add_patch(rect)

        #plot the keyboard
        for i in self.keylist:
            ax.plot(self.keylist[i]['center'][0], -self.keylist[i]['center'][1], marker='.', color='whitesmoke')
            ax.text(self.keylist[i]['center'][0], -self.keylist[i]['center'][1], self.keylist[i]['letter'],
                    horizontalalignment='center',
                    verticalalignment='center',fontsize=16, color='grey')
            rect = Rectangle((self.keylist[i]['bbox']['left'],-self.keylist[i]['bbox']['bottom']),
                             self.keylist[i]['xlen'],-self.keylist[i]['ylen'],
                             linewidth=1,edgecolor='grey',facecolor='whitesmoke')
            ax.add_patch(rect)

        plt.show()
