import numpy as np
import pylab as plt
import os
from optparse import OptionParser

def readonestep(f,data,labels):
    headsplit = f.readline().split(' ')
    if len(headsplit)==1: return True
    #else: print headsplit
    data['step'].append(int(headsplit[1][:-1]))
    data['time'].append(float(headsplit[3][:-1]))
    for label in labels:
        line = f.readline()
        data[label].append(float(line.split()[1]))
    line = f.readline()
    return False

if __name__=="__main__":
    parser = OptionParser()
    parser.add_option('-p','--percent',action='store_true',dest='percentplot',
                      default=False,help='plot percentages')
    options,args = parser.parse_args()
    path = args[0]
    if not os.path.exists(path):
        sys.exit(path+" not valid")
    data = {}
    data['step']=[]; data['time'] = []
    labels = ['total','treegrav',
              'treebuild','treeupdate','treewalk','treecomm','treeimbal',
              'pmgrav','sph','density','denscomm','densimbal','hydrofrc',
              'hydrocomm','hydmisc','mydnetwork','hydimbal','hmaxupdate',
              'domain','potential','predict','kicks','i/o','peano','sfrcool',
              'blackholes','fof/subfind','smoothing','hotngbs','weights_hot',
              'enrich_hot','weights_cold','enrich_cold','cs_misc','misc']
    for label in labels:
        data[label] = []
    f = open(path)
    filedone = False
    while not filedone:
        filedone = readonestep(f,data,labels)
    f.close()
    for key,val in data.items():
        data[key] = np.array(val)
    
    plt.figure(); ax = plt.gca()
    xlab = 'step' #step or time
    x = data[xlab]; ax.set_xlabel(xlab)
    labelstoplot = ['treegrav','pmgrav','domain']
    colors = ['b','g','r','k']; alpha = 0.2
    assert len(colors) == len(labelstoplot)+1
    datatoplot = [np.zeros(len(x))]
    for label in labelstoplot:
        datatoplot.append(data[label])
    datatoplot = np.array(datatoplot)
    datatoplot = np.cumsum(datatoplot,axis=0)

    if options.percentplot:
        for i,label in enumerate(labelstoplot):
            datatoplot[i+1,:] = datatoplot[i+1,:]/data['total']

    for i,label in enumerate(labelstoplot):
        ax.fill_between(x,datatoplot[i,:],datatoplot[i+1,:],
                        facecolor=colors[i],alpha=alpha)
        ax.plot(x,datatoplot[i+1,:],colors[i],label=label)

    if options.percentplot:
        ax.fill_between(x,datatoplot[-1,:],1,
                        facecolor=colors[-1],alpha=alpha)
        ax.plot(x,np.zeros(len(x))+1.0,colors[-1],label='total')
        ax.set_ylabel('fraction')
        ax.set_ylim((0,1.1))
    else:
        ax.fill_between(x,datatoplot[-1,:],data['total'],
                        facecolor=colors[-1],alpha=alpha)
        ax.plot(x,data['total'],colors[-1],label='total')
        ax.set_ylabel('cputime (sec?)')
    ax.set_xlim((0,np.max(x)))
    handles,labels = ax.get_legend_handles_labels()
    ax.legend(handles[::-1],labels[::-1],loc='lower right')
    plt.tight_layout()
    plt.show()
