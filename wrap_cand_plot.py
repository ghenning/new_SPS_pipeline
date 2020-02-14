import numpy as np
import subprocess
import os
import struct

def header(afile):
    inread = ""
    while True:
        tmp = afile.read(1)
        inread = inread + tmp 
        flag = inread.find('HEADER_END')
        if flag != -1: 
            break
    return inread

def get_headparam(head, parlist):
    how2parse={
        'nchans': ('i',4),
        'tsamp': ('d',8),
        'foff': ('d',8),
        'fch1': ('d',8),
        'tstart': ('d',8),
        'ibeam': ('i',4)
    }   
    n = 0 
    for i in parlist:
        i1 = head.find(i)
        i2 = i1 + len(i)
        nbytes = how2parse[i][1]
        cstr = how2parse[i][0]

        val = struct.unpack(cstr, head[i2:i2+nbytes])[0]
        parlist[n] = val 
        n += 1
        return parlist


def plot_cands(FIL,MASK,DIR,CANDFILE):
        
    # load file
    data = np.loadtxt(CANDFILE)
    if not data.any():
        str2return = "No cands to plot"
        print "{}".format(str2return)
        return 0 

    # fix weird behaviour with one-liners
    if np.ndim(data)==1:
        data = np.reshape(data,(1,len(data)))

    # read header 
    with open(FIL,'r') as F:
        head = header(F)

    # file parameters
    ftop = get_headparam(head,['fch1'])[0]
    fchan = get_headparam(head,['foff'])[0]
    nchan = get_headparam(head,['nchans'])[0]
    samptime = get_headparam(head,['nchans'])[0]

    # scrunch parameters
    fscrunch = 512
    tscrunc = 4

    # plot directory
    plt_dir = os.path.join(DIR,"cand_plots")
    
    # loop through candidates and plot each one
    for cand in data:
        DM = cand[0]
        T = cand[3] 
        
        # call generalplotter.py 
        subproces.check_call(["python","generalplotter.py",
            "--ftop",ftop,
            "--fchan",fchan,
            "--nchan",nchan,
            "--samptime",samptime,
            "--data",FIL,
            "--fscrunch",str(fscrunch),
            "--tscrunch",str(tscrunch),
            "--out",plt_dir,
            "--dm",DM,
            "--samp",T,
            "--mask",MASK])

