import numpy as np
import pylab as plt
from haloutils import get_foldername,find_halo_paths
import os
import readhalos.readsubf as rsf
import readhalos.readgroup as rg

def check_last_subfind_exists(outpath):
    numsnaps = sum(1 for line in open(outpath+'/ExpansionList'))
    lastsnap = numsnaps - 1; snapstr = str(lastsnap).zfill(3)
    group_tab = os.path.exists(outpath+'/outputs/groups_'+snapstr+'/group_tab_'+snapstr+'.0')
    subhalo_tab = os.path.exists(outpath+'/outputs/groups_'+snapstr+'/subhalo_tab_'+snapstr+'.0')
    return group_tab and subhalo_tab

if __name__=="__main__":
    verbose = False
    halopathlist = find_halo_paths(nrvirlist=[3,4,5,6],levellist=[11,12,13,14],ictype="BB",onlychecklastsnap=True,verbose=False)
    newpathlist = []
    for outpath in halopathlist:
        if check_last_subfind_exists(outpath):
            newpathlist.append(outpath)
        else:
            if verbose:
                print get_foldername(outpath)+' does not have subfind run'
    if verbose:
        print "Total not run:",len(halopathlist)-len(newpathlist)
        print "Number of relevant paths:",len(newpathlist)#,len(halopathlist)-len(newpathlist)
    else:
        print "#haloname groupx groupy groupz subx suby subz"

    for outpath in newpathlist:
        lastsnap = sum(1 for line in open(outpath+'/ExpansionList'))-1
        groups = rg.group_tab(outpath+'/outputs',lastsnap)
        #hires_groups = groups.GroupMassType[:,1]>0
        #print np.array(groups.GroupMassType[hires_groups,1])
        #num_hires_groups = np.sum(hires_groups)
        ## Pick best group by the one with the most hi-res particles
        bestgroup = np.where(groups.GroupMassType[:,1] == np.max(groups.GroupMassType[:,1]))[0]
        if len(bestgroup) != 1:
            raise RuntimeError("wrong number of groups (should be 1): "+strlen(bestgroup))
        bestgroup = bestgroup[0]
        subcat = rsf.subfind_catalog(outpath+'/outputs',lastsnap)
        substart = subcat.group_firstsub[bestgroup]; subnum = subcat.group_nsubs[bestgroup]
        groupcm = groups.GroupCM[bestgroup,:]; subcm = subcat.sub_cm[substart,:] #first one is the largest sub
        if verbose:
            print "--- "+get_foldername(outpath)
            print "Group location:",groups.GroupCM[bestgroup,:]
            print "Largest sub location:",subcat.sub_cm[substart,:] 
        else:
            print get_foldername(outpath),groupcm[0],groupcm[1],groupcm[2],subcm[0],subcm[1],subcm[2]
