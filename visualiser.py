## helper function to visualise generated input stream
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.patches import Rectangle

def plotTaps(taps, keyboard, figlen, figw):

    ##generate distinct colour for each key
    n_colors = len(keyboard.keylist)
    colourdict={}

    keylist = list(keyboard.keylist.keys())

    cmap = cm.get_cmap('tab20')
    for i in range(len(keyboard.keylist)):
        colourdict[keylist[i]]=cmap(i%20)

    ##process input stream
    xvect=[]
    yvect=[]

    xvectdwn=[]
    yvectdwn=[]

    keypress=[]

    for i in range(len(taps)):
        xvect.append(taps[i]['tap']['x'])
        yvect.append(-taps[i]['tap']['y'])
        xvectdwn.append(taps[i]['touchdown']['x'])
        yvectdwn.append(-taps[i]['touchdown']['y'])
        keypress.append(taps[i]['intent'])

    #plot the keyboard
    fig, ax = plt.subplots(figsize=(figlen, figw))

    rect = Rectangle((0,-keyboard.ydim), keyboard.xdim,keyboard.ydim,
                             linewidth=1,edgecolor='black',facecolor='darkgrey')
    ax.add_patch(rect)

    for i in keyboard.keylist:
        ax.plot(keyboard.keylist[i]['center'][0], -keyboard.keylist[i]['center'][1], marker='x', color='whitesmoke')
        ax.text(keyboard.keylist[i]['center'][0], -keyboard.keylist[i]['center'][1], keyboard.keylist[i]['letter'],
                horizontalalignment='center',
                verticalalignment='center',fontsize=16, color='grey')
        rect = Rectangle((keyboard.keylist[i]['bbox']['left'],-keyboard.keylist[i]['bbox']['bottom']),
                         keyboard.keylist[i]['xlen'],-keyboard.keylist[i]['ylen'],
                         linewidth=1,edgecolor='dimgrey',facecolor='whitesmoke')
        ax.add_patch(rect)


    #plot the taps
    #ax.scatter(xvect, yvect, marker='^',  alpha=0.2, color='red')
    #ax.scatter(xvectdwn, yvectdwn, marker='v',  alpha=0.2, color='blue')

    #for k in range(len(xvect)):
    #    xvals = [xvect[k], xvectdwn[k]]
    #    yvals = [yvect[k], yvectdwn[k]]
    #    ax.plot(xvals, yvals, linestyle="--", color='blue', alpha=0.2)

    #plot slide vectors
    for k in range(len(xvect)):
        xvals = [xvectdwn[k], xvect[k]]
        yvals = [yvectdwn[k], yvect[k]]
        ax.plot(xvals, yvals, linestyle="-", linewidth=3, color=colourdict[keypress[k]], alpha=0.5)
        #ax.annotate(text='', xy=(xvectdwn[k],yvectdwn[k]), xytext=(xvect[k],yvect[k]), arrowprops=dict(arrowstyle='<-', color='red', alpha=0.2))
        if k<len(xvect)-1:
            xvals = [xvect[k], xvectdwn[k+1]]
            yvals = [yvect[k], yvectdwn[k+1]]

    ax.set_xlim(-60,1500)
    ax.set_ylim(-1060,200)

    #plot all taps
    #ax.scatter(xvect, yvect, marker='o', alpha=0.3)

    #plot taps by color
    #for k in range(len(xvect)):
    #    ax.scatter(xvectdwn[k],yvectdwn[k],color=colourdict[keypress[k]], marker='o', alpha=0.8)


    #plot ready
    plt.show()
