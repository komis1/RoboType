## helper function to visualise generated input stream
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.patches import Rectangle
import numpy as np
from matplotlib.patches import Ellipse
import matplotlib.transforms as transforms


def confidence_ellipse(x, y, ax, n_std=3.0, facecolor='none', **kwargs):
    """
    Create a plot of the covariance confidence ellipse of *x* and *y*.

    Parameters
    ----------
    x, y : array-like, shape (n, )
        Input data.

    ax : matplotlib.axes.Axes
        The axes object to draw the ellipse into.

    n_std : float
        The number of standard deviations to determine the ellipse's radiuses.

    **kwargs
        Forwarded to `~matplotlib.patches.Ellipse`

    Returns
    -------
    matplotlib.patches.Ellipse
    """
    if x.size != y.size:
        raise ValueError("x and y must be the same size")

    cov = np.cov(x, y)
    pearson = cov[0, 1]/np.sqrt(cov[0, 0] * cov[1, 1])
    # Using a special case to obtain the eigenvalues of this
    # two-dimensional dataset.
    ell_radius_x = np.sqrt(1 + pearson)
    ell_radius_y = np.sqrt(1 - pearson)
    ellipse = Ellipse((0, 0), width=ell_radius_x * 2, height=ell_radius_y * 2,
                      facecolor=facecolor, **kwargs, alpha=0.5)

    # Calculating the standard deviation of x from
    # the squareroot of the variance and multiplying
    # with the given number of standard deviations.
    scale_x = np.sqrt(cov[0, 0]) * n_std
    mean_x = np.mean(x)

    # calculating the standard deviation of y ...
    scale_y = np.sqrt(cov[1, 1]) * n_std
    mean_y = np.mean(y)

    transf = transforms.Affine2D() \
        .rotate_deg(45) \
        .scale(scale_x, scale_y) \
        .translate(mean_x, mean_y)

    ellipse.set_transform(transf + ax.transData)
    return ax.add_patch(ellipse)


def plotTaps(inputstream, keyboard, figlen, figw, mode='slides'):

    ##generate distinct colour for each key
    n_colors = len(keyboard.keylist)
    colourdict={}

    keylist = list(keyboard.keylist.keys())
    
    taps=[]
    for sentence in inputstream:
        taps.extend(sentence['taps'])

    cmap = cm.get_cmap('tab20')
    for i in range(len(keyboard.keylist)):
        colourdict[keylist[i]]=cmap(i%20)

    ##process input stream
    xvect=[]
    yvect=[]

    xvectdwn=[]
    yvectdwn=[]
    
    keypress=[]
    
    tapset={}

    for i in range(len(taps)):
        xvect.append(taps[i]['tap']['x'])
        yvect.append(-taps[i]['tap']['y'])
        xvectdwn.append(taps[i]['touchdown']['x'])
        yvectdwn.append(-taps[i]['touchdown']['y'])
        keypress.append(taps[i]['intent'])
        
        if taps[i]['intent'] not in tapset:
            tapset[taps[i]['intent']]={}
            tapset[taps[i]['intent']]['x']=[]
            tapset[taps[i]['intent']]['y']=[]
        
        tapset[taps[i]['intent']]['x'].append(taps[i]['tap']['x'])
        tapset[taps[i]['intent']]['y'].append(-taps[i]['tap']['y'])
    
    #print(tapset)
            

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

    if mode=='slides':
        #plot slide vectors
        for k in range(len(xvect)):
            xvals = [xvectdwn[k], xvect[k]]
            yvals = [yvectdwn[k], yvect[k]]
            ax.plot(xvals, yvals, linestyle="-", linewidth=3, color=colourdict[keypress[k]], alpha=0.5)
            #ax.annotate(text='', xy=(xvectdwn[k],yvectdwn[k]), xytext=(xvect[k],yvect[k]), arrowprops=dict(arrowstyle='<-', color='red', alpha=0.2))
            if k<len(xvect)-1:
                xvals = [xvect[k], xvectdwn[k+1]]
                yvals = [yvect[k], yvectdwn[k+1]]
                
    else:
        #plot taps by color
        #for k in range(len(xvect)):
        #    ax.scatter(xvectdwn[k],yvectdwn[k],color=colourdict[keypress[k]], marker='o', alpha=0.8)
        #
        for key in tapset:
            ax.scatter(tapset[key]['x'], tapset[key]['y'], color=colourdict[key], marker='.', alpha=0.05)
            confidence_ellipse(np.array(tapset[key]['x']), np.array(tapset[key]['y']), ax, n_std=1.96, edgecolor=colourdict[key], facecolor=colourdict[key])
            
    ax.set_xlim(-60,1500)
    ax.set_ylim(-1060,200)

    #plot all taps
    #ax.scatter(xvect, yvect, marker='o', alpha=0.3)

    


    #plot ready
    plt.show()
