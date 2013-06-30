import numpy as np
import pylab as plt
import readhalos.readsubf as readsubf
import readhalos.readgroup as readgroup
import readsnapshots.readsnap as rs
import readsnapshots.readids as readids
from scipy import interpolate
from scipy import integrate
from alexlib.densityprofile import densityprofile
from alexlib.profilefit import fitNFW,NFWprofile,fitEinasto,EINprofile

#IMPORTANT STUFF
ictype = "ellipsoid"
nparttypes = 1 # Select only high resolution particles
#ROUGH FOF CENTER - need to generalise but depends on environment in each box :|          
haloid = 80609
xcen = 51.24
ycen = 48.28
zcen = 47.30
#haloid = 190897
#xcen = 12.07
#ycen = 77.74
#zcen = 88.08

#LESS IMPORTANT STUFF
hubble = 0.6711
snapnum = 63
#padlist = ['p6','p7','p8','p9','p10']
padlist = ['p6','p7','p8']
reslist = ['l11']
#nvirlist= ['nvir3','nvir4','nvir5','nvir6','nvir7','nvir8','nvir9']
nvirlist= ['nvir3','nvir6','nvir9']
partypelist = np.linspace(1,nparttypes-1,nparttypes)

basedir = "/spacebase/data/AnnaGroup/caterpillar/contamination/halos/halo" + str(haloid)

#AXES
ymin = 10**-1.5
ymax = 10**2.5
xmin = 0.1
xmax = 1000

#SIZE OF FIGURE (MAY NEED TO CHANGE FOR YOUR RES)
figx = 4
figy = 12
fig1 = plt.figure(figsize=(figx,figy))
fig1.subplots_adjust(hspace=0.1)
fig1.subplots_adjust(wspace=0.1)

nwide = len(nvirlist)
nhigh = len(padlist)

figi = 0
for res in reslist:
    for pad in padlist:
        figi += 1
        ax1 = fig1.add_subplot(nhigh,1,figi)
        titlestr = pad
        pltlist = []
        for nvir in nvirlist:
            tmppath = basedir + '/' + ictype + '/' + res + '/' + pad + '/' + nvir + '/outputs'
            filepath = tmppath + "/snapdir_0" + str(snapnum) + "/snap_0" + str(snapnum)
            
            print "+++++++++++++++++++++++++++++++++++"
            print "+PADDING:",pad,"+N*RVIR:",nvir

            s = readsubf.subfind_catalog(tmppath, snapnum)
            mgroup = s.group_m_mean200*10**10/hubble
            rvirgroup = s.group_r_mean200
            xposgroup = s.group_pos[:,0]
            yposgroup = s.group_pos[:,1]
            zposgroup = s.group_pos[:,2]

            #SEARCH WINDOW
            deltapos = 1.5 #Mpc/h

            for inx in xrange(0,len(mgroup)):
                if mgroup[inx] > 8E11:
                    if xposgroup[inx] > xcen-deltapos and xposgroup[inx] < xcen+deltapos:
                        if yposgroup[inx] > ycen-deltapos and yposgroup[inx] < ycen+deltapos:
                            if zposgroup[inx] > zcen-deltapos and zposgroup[inx] < zcen+deltapos:
                                subfhaloid = inx
                                posxFOF = xposgroup[inx]
                                posyFOF = yposgroup[inx]
                                poszFOF = zposgroup[inx]
                                rvirFOF = rvirgroup[inx]
                                massFOF = mgroup[inx]
                                print "!FOUND FOF-GROUP CANDIDATE (MMEAN,X,Y,Z,RMEAN,subfid)!"
                                print '{0:.2e}'.format(float(massFOF)),'{:.2f}'.format(float(posxFOF)),'{:.2f}'.format(float(posyFOF)),'{:.2f}'.format(float(poszFOF)),'{:.2f}'.format(float(rvirFOF)),inx

            # COMPUTE DENSITY PROFILE
            header = rs.snapshot_header(filepath+".0")
            haloparts = readids.subid_file(tmppath,63,s.group_offset[subfhaloid],s.sub_len[s.group_firstsub[subfhaloid]])
            rarr = np.logspace(-5,0,100) #in Mpc
            halopos = s.group_pos[subfhaloid,:]

            rhoarr,p03r = densityprofile(rarr,filepath,header,haloparts,halopos,verbose=True,power03=True)
            p03r = p03r*1000
            r200 = s.group_r_crit200[subfhaloid]*1000

            line, = ax1.plot(rarr*1000.,rhoarr*rarr**2)
            pltlist.append(line)
            ax1.plot([p03r,p03r],[ymin,ymax],'k--')
            ax1.plot([r200,r200],[ymin,ymax],'k-.')

            rrange = np.where(np.logical_and(rarr>p03r/1000,rarr<r200/1000))[0]
            rscale,rhos = fitNFW(rarr[rrange],rhoarr[rrange])
            ax1.plot(rarr*1000,rarr**2*NFWprofile(rarr,rscale,rhos),'k:')
            r2,rho2,alpha = fitEinasto(rarr[rrange],rhoarr[rrange])
            ax1.plot(rarr*1000,rarr**2*EINprofile(rarr,r2,rho2,alpha),'r:')

        ax1.plot([1,1],[ymin,ymax],'k:')
        ax1.set_xlim([xmin,xmax])
        ax1.set_ylim([ymin,ymax])
        ax1.set_xscale('log')
        ax1.set_yscale('log')
        
        ax1.text(0.95, 0.95,titlestr,
                 horizontalalignment='right',
                 verticalalignment='top',
                 color='black',
                 weight='bold',
                 transform = ax1.transAxes)
        
        #if figi == 29:
        if figi == 3:
            ax1.set_xlabel(r'$\mathrm{r\ [kpc/h]}$',size=14)
        else:
            ax1.set_xticklabels([])
        
        #if figi == 1 or figi == 8 or figi == 15 or figi == 22 or figi == 29:
        if True:
            ax1.set_ylabel(r'$\mathrm{r^2 \rho(r)\ [10^{10}M_\odot/Mpc]}$',size=14)
        else:
            ax1.set_yticklabels([])

    plt.legend(pltlist,nvirlist,loc="lower left")
fig1.savefig(ictype + '-h' + str(haloid) + '-NFWprofiles.pdf',bbox_inches='tight')
